from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlmodel import Session, select
from telethon import TelegramClient
from telethon.sessions import StringSession
from app.models import Bot, Agendamento, LogExecucao
from app.core.config import templates
from app.core.deps import get_session
from worker import aplicar_processamento_mensagem

router = APIRouter(prefix="/agendamentos", tags=["agendamentos"])

@router.get("", response_class=HTMLResponse)
async def listar_agendamentos(request: Request, session: Session = Depends(get_session)):
    agendamentos = session.exec(select(Agendamento)).all()
    bots = session.exec(select(Bot)).all()
    return templates.TemplateResponse("agendamentos.html", {"request": request, "agendamentos": agendamentos, "bots": bots})

@router.post("/criar")
async def criar_agendamento(
    nome: str = Form(...), origem: str = Form(...), destino: str = Form(...),
    msg_id_atual: int = Form(...), tipo_envio: str = Form(...), horario: str = Form(...),
    bot_id: int = Form(...), 
    filtro: str = Form(None), substituto: str = Form(None), 
    bloqueios: str = Form(None), somente_se_tiver: str = Form(None),
    filtro_midia: str = Form("todos"),
    session: Session = Depends(get_session)
):
    novo = Agendamento(
        nome=nome, origem=origem, destino=destino, msg_id_atual=msg_id_atual,
        tipo_envio=tipo_envio, horario=horario, bot_id=bot_id, 
        filtro=filtro, substituto=substituto, bloqueios=bloqueios,
        somente_se_tiver=somente_se_tiver, filtro_midia=filtro_midia, ativo=True
    )
    session.add(novo); session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

@router.get("/editar/{id}", response_class=HTMLResponse)
async def form_editar_agendamento(request: Request, id: int, session: Session = Depends(get_session)):
    ag = session.get(Agendamento, id)
    bots = session.exec(select(Bot)).all()
    if not ag:
        return RedirectResponse(url="/agendamentos", status_code=303)
    return templates.TemplateResponse("editar_agendamento.html", {"request": request, "ag": ag, "bots": bots})

@router.post("/editar/{id}")
async def atualizar_agendamento(
    id: int,
    nome: str = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    msg_id_atual: int = Form(...),
    tipo_envio: str = Form(...),
    horario: str = Form(...),
    bot_id: int = Form(...),
    filtro: str = Form(None),
    substituto: str = Form(None),
    bloqueios: str = Form(None),
    somente_se_tiver: str = Form(None),
    filtro_midia: str = Form("todos"),
    session: Session = Depends(get_session)
):
    ag = session.get(Agendamento, id)
    if ag:
        ag.nome = nome
        ag.origem = origem
        ag.destino = destino
        ag.msg_id_atual = msg_id_atual
        ag.tipo_envio = tipo_envio
        ag.horario = horario
        ag.bot_id = bot_id
        ag.filtro = filtro
        ag.substituto = substituto
        ag.bloqueios = bloqueios
        ag.somente_se_tiver = somente_se_tiver
        ag.filtro_midia = filtro_midia
        session.add(ag)
        session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

@router.get("/deletar/{id}")
async def deletar_agendamento(id: int, session: Session = Depends(get_session)):
    item = session.get(Agendamento, id)
    if item: session.delete(item); session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

@router.get("/toggle/{id}")
async def toggle_agendamento(id: int, session: Session = Depends(get_session)):
    item = session.get(Agendamento, id)
    if item:
        item.ativo = not item.ativo
        session.add(item)
        session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

@router.get("/enviar_now/{id}")
async def enviar_agendamento_agora(id: int, session: Session = Depends(get_session)):
    ag = session.get(Agendamento, id)
    if not ag or not ag.bot:
        return RedirectResponse(url="/agendamentos", status_code=303)
    
    bot = ag.bot
    client = None
    try:
        client = TelegramClient(StringSession(bot.session_string), bot.api_id, bot.api_hash)
        await client.connect()
        
        if not await client.is_user_authorized():
            if bot.tipo == "bot" and bot.bot_token:
                await client.start(bot_token=bot.bot_token)
                bot.session_string = client.session.save()
                session.add(bot)
                session.commit()
            else:
                raise Exception("Bot não autorizado. Verifique a sessão.")
        
        def get_chat_list(chat_id):
            if not chat_id: return []
            parts = [p.strip() for p in str(chat_id).split(',')]
            res = []
            for p in parts:
                if not p: continue
                try: res.append(int(p))
                except ValueError: res.append(p)
            return res

        origens = get_chat_list(ag.origem)
        destinos = get_chat_list(ag.destino)
        
        if not origens or not destinos:
            raise Exception("Origem ou Destino inválidos.")
            
        origem_id = origens[0]
        
        try:
            await client.get_entity(origem_id)
        except Exception as e:
            print(f"⚠️ Aviso: Falha ao resolver entidade {origem_id}: {e}")
        
        msg = await client.get_messages(origem_id, ids=ag.msg_id_atual)
        if msg:
            msg_proc, erro_proc = aplicar_processamento_mensagem(
                msg, ag.nome, ag.bloqueios, ag.somente_se_tiver, 
                ag.filtro, ag.substituto, ag.filtro_midia
            )
            
            if msg_proc:
                for d in destinos:
                    await client.send_message(d, msg_proc)
                
                ag.msg_id_atual += 1
                session.add(ag)
                
                log = LogExecucao(
                    bot_id=bot.id, bot_nome=bot.nome, origem=str(ag.origem),
                    destino=str(ag.destino), status="Sucesso", 
                    mensagem=f"Envio Manual: Agendamento '{ag.nome}' (ID {msg.id}) enviado para {len(destinos)} destino(s)."
                )
                session.add(log)
                session.commit()
            else:
                log = LogExecucao(
                    bot_id=bot.id, bot_nome=bot.nome, origem=str(ag.origem),
                    destino=str(ag.destino), status="BLOQUEADO", 
                    mensagem=f"Envio Manual: '{ag.nome}' bloqueado: {erro_proc}"
                )
                session.add(log)
                session.commit()
        else:
            raise Exception(f"Mensagem ID {ag.msg_id_atual} não encontrada na origem.")
            
    except Exception as e:
        print(f"Erro no envio manual: {e}")
        log = LogExecucao(
            bot_id=bot.id, bot_nome=bot.nome, origem=str(ag.origem),
            destino=str(ag.destino), status="Erro", 
            mensagem=f"Erro no envio manual: {str(e)}"
        )
        session.add(log)
        session.commit()
    finally:
        if client:
            await client.disconnect()

    return RedirectResponse(url="/agendamentos", status_code=303)
