import asyncio
import random
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from sqlmodel import Session, select
from database import engine, Regra, LogExecucao, Agendamento, Configuracao
import re
import requests
import hashlib
import json
import time


# --- CLASSE API SHOPEE ---
class ShopeeAPI:
    def __init__(self, app_id: str, secret: str):
        self.app_id = app_id
        self.secret = secret
        self.base_url = "https://open-api.affiliate.shopee.com.br"
        self.endpoint = "/graphql"

    def _gen_sig(self, payload: str) -> tuple[str, str]:
        ts = str(int(time.time()))
        msg = f"{self.app_id}{ts}{payload}{self.secret}"
        sig = hashlib.sha256(msg.encode('utf-8')).hexdigest()
        return sig, ts

    def _auth_header(self, payload: str):
        sig, ts = self._gen_sig(payload)
        auth_h = f"SHA256 Credential={self.app_id}, Timestamp={ts}, Signature={sig}"
        return {"Authorization": auth_h, "Content-Type": "application/json"}

    def gen_link(self, url: str) -> str:
        sub_ids = ["conekta", "bot"] 
        gq = {"query": f'''mutation {{ generateShortLink(input: {{ originUrl: "{url}", subIds: {json.dumps(sub_ids)} }}) {{ shortLink }} }}'''}
        payload = json.dumps(gq)
        headers = self._auth_header(payload)
        try:
            resp = requests.post(f"{self.base_url}{self.endpoint}", headers=headers, json=gq, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                link = data.get("data", {}).get("generateShortLink", {}).get("shortLink")
                if link: return link
                else: print(f"   ⚠️ [Shopee] API 200 sem link: {data}")
            else: print(f"   ⚠️ [Shopee] Erro {resp.status_code}: {resp.text}")
        except Exception as e: print(f"   ❌ [Shopee] Exceção: {e}")
        return None

class BotWorker:
    def __init__(self, db_bot):
        self.bot_id = db_bot.id
        self.nome = db_bot.nome
        self.api_id = db_bot.api_id
        self.api_hash = db_bot.api_hash
        self.session_string = db_bot.session_string
        self.client = None
        self.fila_envio = asyncio.Queue()
        self.handlers_ativos = [] 
        self.hash_regras_atual = "" 
        
        self.current_shopee_id = None
        self.current_shopee_secret = None
        self.shopee = None
        
        # Inicializa buscando do banco global
        self.atualizar_credenciais_sync()

    # --- FUNÇÕES AUXILIARES ---
    def atualizar_credenciais_sync(self):
        try:
            with Session(engine) as session:
                config = session.exec(select(Configuracao)).first()
                if config and config.shopee_app_id and config.shopee_app_secret:
                    self.current_shopee_id = config.shopee_app_id
                    self.current_shopee_secret = config.shopee_app_secret
                    self.shopee = ShopeeAPI(self.current_shopee_id, self.current_shopee_secret)
                    print(f"   ✅ [{self.nome}] API Shopee carregada (Global).")
                else:
                    self.shopee = None
        except Exception as e:
            print(f"   ❌ Erro lendo config Shopee: {e}")

    async def atualizar_credenciais_loop(self):
        try:
            with Session(engine) as session:
                config = session.exec(select(Configuracao)).first()
                novo_id = config.shopee_app_id if config else None
                novo_secret = config.shopee_app_secret if config else None

                if (novo_id != self.current_shopee_id) or (novo_secret != self.current_shopee_secret):
                    print(f"🔄 [{self.nome}] Configuração Shopee mudou. Atualizando...")
                    self.current_shopee_id = novo_id
                    self.current_shopee_secret = novo_secret
                    if novo_id and novo_secret: self.shopee = ShopeeAPI(novo_id, novo_secret)
                    else: self.shopee = None
        except Exception as e: print(f"❌ Erro Hot Reload Config Shopee: {e}")

    def processar_chat_id(self, chat_id):
        try:
            return int(chat_id)
        except ValueError:
            return chat_id

    def registrar_log(self, origem, destino, status, mensagem):
        try:
            with Session(engine) as session:
                novo_log = LogExecucao(
                    bot_id=self.bot_id, bot_nome=self.nome, origem=str(origem),
                    destino=str(destino), status=status, mensagem=mensagem
                )
                session.add(novo_log)
                session.commit()
        except Exception as e:
            print(f"Erro ao salvar log: {e}")

    # --- TAREFA 1: CONSUMIDOR DA FILA ---
    async def loop_processamento_fila(self):
        print(f"   🐢 [{self.nome}] Fila de envio iniciada...")
        while True:
            item = await self.fila_envio.get()
            destino, mensagem_original, regra_nome, log_origem = item
            try:
                await self.client.send_message(destino, mensagem_original)
                msg_log = f"'{regra_nome}': Enviada (Restam {self.fila_envio.qsize()})"
                print(f"   🚀 [{self.nome}] {msg_log}")
                self.registrar_log(log_origem, destino, "Sucesso", msg_log)
                tempo_espera = random.uniform(2.0, 5.0)
                await asyncio.sleep(tempo_espera)
            except Exception as e:
                print(f"   ❌ Erro no envio: {e}")
                self.registrar_log(log_origem, destino, "Erro", str(e))
            finally:
                self.fila_envio.task_done()

    # --- LÓGICA SHOPEE ---
    async def converter_links_shopee(self, texto):
        if not texto or not self.shopee: return texto
        
        regex = r'https?://(?:s\.)?shopee\.com(?:\.br)?/[^\s\)\]\"]+'
        links = re.findall(regex, texto)
        if not links: return texto
        
        novo_texto = texto
        for link in links:
            novo_link = await asyncio.to_thread(self.shopee.gen_link, link)
            if novo_link:
                novo_texto = novo_texto.replace(link, novo_link)
        return novo_texto

    # --- FUNÇÃO CENTRAL DE PROCESSAMENTO ---
    def processar_mensagem(self, message, r_nome, r_bloqueios, r_somente, r_filtro, r_sub):
        try:
            texto_msg = message.text or ""
            
            # 1. LÓGICA DE BLACKLIST (Bloqueio)
            if r_bloqueios:
                termos = [t.strip() for t in r_bloqueios.split(',')]
                for termo in termos:
                    if termo and re.search(termo, texto_msg, re.IGNORECASE):
                        print(f"   🚫 [{self.nome}] Regra/Agenda '{r_nome}': BLOQUEADO (Match: '{termo}')")
                        return None, f"Match proibido: {termo}"

            # 2. LÓGICA DE WHITELIST COM REGEX
            if r_somente:
                termos_obrigatorios = [t.strip() for t in r_somente.split(',')]
                encontrou = False
                for termo in termos_obrigatorios:
                    if not termo: continue
                    try:
                        if re.search(termo, texto_msg, re.IGNORECASE):
                            encontrou = True
                            break 
                    except re.error:
                        if termo.lower() in texto_msg.lower():
                            encontrou = True
                            break
                
                if not encontrou:
                    print(f"   ⏭️ [{self.nome}] Regra/Agenda '{r_nome}': Ignorada (Whitelist não bateu)")
                    return None, "Whitelist não bateu"

            # 3. Substituição
            if texto_msg and r_filtro and r_sub:
                try:
                    message.text = re.sub(r_filtro, r_sub, texto_msg, flags=re.IGNORECASE)
                except Exception as e:
                    print(f"   ❌ Erro Regex sub: {e}")
            
            return message, None

        except Exception as e:
            return None, f"Erro processamento: {str(e)}"

    # --- TAREFA 2: MONITOR DE REGRAS ---
    async def carregar_regras(self):
        with Session(engine) as session:
            statement = select(Regra).where(Regra.bot_id == self.bot_id, Regra.ativo == True)
            regras = session.exec(statement).all()
            return [{"id": r.id, "origem": r.origem, "destino": r.destino, "nome": r.nome, 
                     "filtro": r.filtro, "substituto": r.substituto, 
                     "bloqueios": r.bloqueios,
                     "somente_se_tiver": r.somente_se_tiver,
                     "converter_shopee": r.converter_shopee} for r in regras]

    async def aplicar_regras(self):
        regras = await self.carregar_regras()
        hash_novo = str(regras)
        
        if hash_novo == self.hash_regras_atual:
            return 
            
        print(f"🔄 [{self.nome}] Atualizando regras...")
        for handler in self.handlers_ativos:
            self.client.remove_event_handler(handler)
        self.handlers_ativos.clear()
        
        for regra in regras:
            print(f"   🔎 Regra '{regra['nome']}' carregada.")
            
            origem = self.processar_chat_id(regra['origem'])
            destino = self.processar_chat_id(regra['destino'])
            
            async def handler(event, d=destino, o=origem, r_nome=regra['nome'], 
                            r_filtro=regra['filtro'], r_sub=regra['substituto'], 
                            r_bloqueios=regra['bloqueios'],
                            r_somente=regra['somente_se_tiver'],
                            r_shopee=regra['converter_shopee']):
                
                # Conversão Shopee antes do processamento principal
                if r_shopee:
                    event.message.text = await self.converter_links_shopee(event.message.text)

                msg_processada, erro = self.processar_mensagem(
                    event.message, r_nome, r_bloqueios, r_somente, r_filtro, r_sub
                )
                
                if msg_processada:
                    print(f"   📥 [{self.nome}] Recebido. Fila...")
                    await self.fila_envio.put( (d, msg_processada, r_nome, o) )
                elif erro and "BLOQUEADO" in erro:
                    self.registrar_log(o, d, "BLOQUEADO", erro)

            self.client.add_event_handler(handler, events.NewMessage(chats=origem))
            self.handlers_ativos.append(handler)

        self.hash_regras_atual = hash_novo

    async def monitorar_regras_loop(self):
        while True:
            try:
                await self.atualizar_credenciais_loop()
                await self.aplicar_regras()
            except Exception as e:
                print(f"❌ Erro Hot Reload: {e}")
            await asyncio.sleep(10)

    # --- TAREFA 3: AGENDADOR ---
    async def verificar_agendamentos_loop(self):
        print(f"   ⏰ [{self.nome}] Agendador ativado.")
        while True:
            try:
                agora = datetime.now().strftime("%H:%M")
                segundos_para_proximo_minuto = 60 - datetime.now().second
                
                with Session(engine) as session:
                    agendamentos = session.exec(select(Agendamento).where(Agendamento.bot_id == self.bot_id, Agendamento.ativo == True)).all()
                    for ag in agendamentos:
                        lista_horarios = [h.strip() for h in ag.horario.split(',')]
                        if agora in lista_horarios:
                            print(f"   ⏰ Executando agendamento: {ag.nome} ({agora})")
                            origem_id = self.processar_chat_id(ag.origem)
                            destino_id = self.processar_chat_id(ag.destino)
                            try:
                                # Lógica de Pular Bloqueados (Somente para Sequencial)
                                max_tentativas = 10 if ag.tipo_envio == "sequencial" else 1
                                foi_enviado_ou_fixo = False

                                for tentativa in range(max_tentativas):
                                    msg = await self.client.get_messages(origem_id, ids=ag.msg_id_atual)
                                    
                                    if not msg:
                                        print(f"      ⚠️ Msg {ag.msg_id_atual} não encontrada.")
                                        if ag.tipo_envio == "sequencial":
                                            ag.msg_id_atual += 1
                                            continue
                                        break

                                    # Aplica filtros e transformações
                                    msg_proc, erro = self.processar_mensagem(
                                        msg, ag.nome, ag.bloqueios, ag.somente_se_tiver,
                                        ag.filtro, ag.substituto
                                    )
                                    
                                    if msg_proc:
                                        await self.fila_envio.put((destino_id, msg_proc, f"Agenda: {ag.nome}", ag.origem))
                                        if ag.tipo_envio == "sequencial":
                                            ag.msg_id_atual += 1
                                        foi_enviado_ou_fixo = True
                                        break
                                    else:
                                        # Foi bloqueado por filtro
                                        if erro and "BLOQUEADO" in erro:
                                            self.registrar_log(ag.origem, destino_id, "BLOQUEADO", erro)
                                        
                                        if ag.tipo_envio == "sequencial":
                                            print(f"      ⏭️  ID {ag.msg_id_atual} bloqueado. Pulando para o próximo...")
                                            ag.msg_id_atual += 1
                                            # Continua o loop para a próxima tentativa
                                        else:
                                            break # Fixo não pula
                                
                                if ag.tipo_envio == "sequencial":
                                    session.add(ag)
                                    session.commit()
                            except Exception as e:
                                print(f"      ❌ Erro: {e}")
            except Exception as e:
                print(f"❌ Erro Crítico Agendador: {e}")
            await asyncio.sleep(segundos_para_proximo_minuto)

    async def start(self):
        print(f"🔄 Iniciando {self.nome}...")
        try:
            self.client = TelegramClient(StringSession(self.session_string), self.api_id, self.api_hash)
            await self.client.connect()
            if not await self.client.is_user_authorized():
                print(f"❌ {self.nome} não autorizado!")
                return
            me = await self.client.get_me()
            print(f"✅ {self.nome} conectado (@{me.username})")
            
            asyncio.create_task(self.monitorar_regras_loop())
            asyncio.create_task(self.loop_processamento_fila())
            asyncio.create_task(self.verificar_agendamentos_loop())

            await self.client.run_until_disconnected()
        except Exception as e:
            print(f"❌ Erro crítico: {e}")

    async def stop(self):
        if self.client:
            await self.client.disconnect()