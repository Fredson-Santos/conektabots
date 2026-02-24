from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from database import engine, Bot, Regra, LogExecucao, Agendamento, Configuracao, create_db_and_tables

# Cache temporário de login
TEMP_CLIENTS = {}

# Inicializa o banco de dados
create_db_and_tables()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_session():
    with Session(engine) as session:
        yield session

# --- ROTAS PRINCIPAIS ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    bots = session.exec(select(Bot)).all()
    logs = session.exec(select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)).all()
    
    # Verifica se tem configuração da Shopee
    config = session.exec(select(Configuracao)).first()
    aviso_shopee = False
    if not config or not config.shopee_app_id:
        aviso_shopee = True
        
    return templates.TemplateResponse("index.html", {
        "request": request, "bots": bots, "logs": logs, "aviso_shopee": aviso_shopee
    })

# --- CONFIGURAÇÕES GLOBAIS ---

@app.get("/configuracoes", response_class=HTMLResponse)
async def ver_configuracoes(request: Request, session: Session = Depends(get_session)):
    config = session.exec(select(Configuracao)).first()
    return templates.TemplateResponse("configuracoes.html", {"request": request, "config": config})

@app.post("/configuracoes/salvar")
async def salvar_configuracoes(
    shopee_app_id: str = Form(""),
    shopee_app_secret: str = Form(""),
    session: Session = Depends(get_session)
):
    config = session.exec(select(Configuracao)).first()
    if not config:
        config = Configuracao(shopee_app_id=shopee_app_id, shopee_app_secret=shopee_app_secret)
        session.add(config)
    else:
        config.shopee_app_id = shopee_app_id
        config.shopee_app_secret = shopee_app_secret
        session.add(config)
    
    session.commit()
    return RedirectResponse(url="/", status_code=303)

# --- GESTÃO DE BOTS (NOVO) ---

@app.get("/bots/adicionar", response_class=HTMLResponse)
async def form_adicionar_bot(request: Request):
    return templates.TemplateResponse("adicionar_bot.html", {"request": request})

@app.post("/bots/criar")
async def criar_bot(
    nome: str = Form(...),
    tipo: str = Form(...),
    api_id: str = Form(...),
    api_hash: str = Form(...),
    bot_token: str = Form(None),
    phone: str = Form(None),
    session_string: str = Form(None),
    session: Session = Depends(get_session)
):
    # Lógica simples: Se for bot, usamos o token como session_string (padrão Telethon para bots)
    # Se for user, o usuário deve ter colado a string ou usaremos o phone (mas login web é complexo, ideal é colar string)
    
    sessao_final = session_string
    if tipo == "bot" and not session_string:
        sessao_final = None # O worker vai logar usando o token direto na hora do start
    
    novo_bot = Bot(
        nome=nome,
        api_id=api_id,
        api_hash=api_hash,
        tipo=tipo,
        bot_token=bot_token,
        phone=phone,
        session_string=sessao_final,
        ativo=True
    )
    session.add(novo_bot)
    session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/bots/deletar/{id}")
async def deletar_bot(id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)
    if bot:
        # Nota: Ao deletar o bot, as regras e agendamentos filhos podem ficar órfãos ou dar erro
        # dependendo do banco. O ideal seria deletar tudo em cascata, mas vamos deletar o bot por enquanto.
        session.delete(bot)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/bots/toggle/{id}")
async def toggle_bot(id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)
    if bot:
        bot.ativo = not bot.ativo
        session.add(bot)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/bots/editar/{id}", response_class=HTMLResponse)
async def form_editar_bot(request: Request, id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)
    if not bot:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("editar_bot.html", {"request": request, "bot": bot})

@app.post("/bots/editar/{id}")
async def atualizar_bot(
    id: int,
    nome: str = Form(...),
    tipo: str = Form(...),
    api_id: str = Form(...),
    api_hash: str = Form(...),
    bot_token: str = Form(None),
    phone: str = Form(None),
    session_string: str = Form(None),
    session: Session = Depends(get_session)
):
    bot = session.get(Bot, id)
    if bot:
        bot.nome = nome
        bot.tipo = tipo
        bot.api_id = api_id
        bot.api_hash = api_hash
        bot.bot_token = bot_token
        bot.phone = phone
        
        # Só atualiza a sessão se o usuário colou uma nova. 
        # Se deixar em branco, mantém a que já estava funcionando.
        if session_string and session_string.strip():
            bot.session_string = session_string
            
        session.add(bot)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

# --- LOGIN USERBOT (NOVO) ---

@app.post("/bots/userbot/enviar-codigo", response_class=HTMLResponse)
async def userbot_enviar_codigo(
    request: Request, 
    nome: str = Form(...), 
    api_id: str = Form(...), 
    api_hash: str = Form(...), 
    phone: str = Form(...)
):
    try:
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            TEMP_CLIENTS[phone] = {"client": client, "nome": nome, "api_id": api_id, "api_hash": api_hash}
            return templates.TemplateResponse("adicionar_bot.html", {
                "request": request, 
                "step": 2, 
                "phone": phone, 
                "msg": f"Código enviado para {phone}."
            })
        else:
            return templates.TemplateResponse("adicionar_bot.html", {
                "request": request, 
                "step": 1, 
                "error": "Já logado."
            })
    except Exception as e:
        return templates.TemplateResponse("adicionar_bot.html", {
            "request": request, 
            "step": 1, 
            "error": f"Erro: {str(e)}"
        })

@app.post("/bots/userbot/validar-codigo", response_class=HTMLResponse)
async def userbot_validar_codigo(
    request: Request, 
    phone: str = Form(...), 
    code: str = Form(...), 
    session: Session = Depends(get_session)
):
    if phone not in TEMP_CLIENTS:
        return templates.TemplateResponse("adicionar_bot.html", {
            "request": request, 
            "step": 1, 
            "error": "Sessão expirada."
        })
    
    data = TEMP_CLIENTS[phone]
    client = data["client"]
    try:
        await client.sign_in(phone, code)
        sessao = client.session.save()
        await client.disconnect()
        del TEMP_CLIENTS[phone]
        
        novo = Bot(
            nome=data["nome"], 
            api_id=data["api_id"], 
            api_hash=data["api_hash"], 
            phone=phone, 
            tipo="user", 
            session_string=sessao, 
            ativo=True
        )
        session.add(novo)
        session.commit()
        return RedirectResponse(url="/", status_code=303)
    except SessionPasswordNeededError:
        return templates.TemplateResponse("adicionar_bot.html", {
            "request": request, 
            "step": 3, 
            "phone": phone, 
            "msg": "Digite sua senha 2FA."
        })
    except Exception as e:
        return templates.TemplateResponse("adicionar_bot.html", {
            "request": request, 
            "step": 2, 
            "phone": phone, 
            "error": str(e)
        })

@app.post("/bots/userbot/validar-senha")
async def userbot_validar_senha(
    phone: str = Form(...), 
    password: str = Form(...), 
    session: Session = Depends(get_session)
):
    if phone not in TEMP_CLIENTS:
        return RedirectResponse(url="/bots/adicionar", status_code=303)
    
    data = TEMP_CLIENTS[phone]
    client = data["client"]
    try:
        await client.sign_in(password=password)
        sessao = client.session.save()
        await client.disconnect()
        del TEMP_CLIENTS[phone]
        
        novo = Bot(
            nome=data["nome"], 
            api_id=data["api_id"], 
            api_hash=data["api_hash"], 
            phone=phone, 
            tipo="user", 
            session_string=sessao, 
            ativo=True
        )
        session.add(novo)
        session.commit()
        return RedirectResponse(url="/", status_code=303)
    except:
        return RedirectResponse(url="/bots/adicionar", status_code=303)

# --- REGRAS ---

@app.get("/regras", response_class=HTMLResponse)
async def listar_regras(request: Request, session: Session = Depends(get_session)):
    regras = session.exec(select(Regra)).all()
    bots = session.exec(select(Bot)).all()
    return templates.TemplateResponse("regras.html", {"request": request, "regras": regras, "bots": bots})

@app.post("/regras/criar")
async def criar_regra(
    nome: str = Form(...), origem: str = Form(...), destino: str = Form(...), bot_id: int = Form(...),
    filtro: str = Form(None), substituto: str = Form(None), bloqueios: str = Form(None), somente_se_tiver: str = Form(None),
    converter_shopee: bool = Form(False),
    session: Session = Depends(get_session)
):
    nova_regra = Regra(
        nome=nome, origem=origem, destino=destino, bot_id=bot_id,
        filtro=filtro, substituto=substituto, bloqueios=bloqueios, somente_se_tiver=somente_se_tiver, 
        converter_shopee=converter_shopee, ativo=True
    )
    session.add(nova_regra)
    session.commit()
    return RedirectResponse(url="/regras", status_code=303)

@app.get("/regras/toggle/{id}")
async def toggle_regra(id: int, session: Session = Depends(get_session)):
    regra = session.get(Regra, id)
    if regra:
        regra.ativo = not regra.ativo
        session.add(regra)
        session.commit()
    return RedirectResponse(url="/regras", status_code=303)

@app.get("/regras/deletar/{id}")
async def deletar_regra(id: int, session: Session = Depends(get_session)):
    regra = session.get(Regra, id)
    if regra: session.delete(regra); session.commit()
    return RedirectResponse(url="/regras", status_code=303)

@app.get("/regras/editar/{id}", response_class=HTMLResponse)
async def form_editar_regra(request: Request, id: int, session: Session = Depends(get_session)):
    regra = session.get(Regra, id)
    bots = session.exec(select(Bot)).all()
    if not regra:
        return RedirectResponse(url="/regras", status_code=303)
    return templates.TemplateResponse("editar_regra.html", {"request": request, "regra": regra, "bots": bots})

@app.post("/regras/editar/{id}")
async def atualizar_regra(
    id: int,
    nome: str = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    bot_id: int = Form(...),
    filtro: str = Form(None), 
    substituto: str = Form(None),
    bloqueios: str = Form(None), 
    somente_se_tiver: str = Form(None),
    converter_shopee: bool = Form(False),
    session: Session = Depends(get_session)
):
    regra = session.get(Regra, id)
    if regra:
        regra.nome = nome
        regra.origem = origem
        regra.destino = destino
        regra.bot_id = bot_id
        regra.filtro = filtro
        regra.substituto = substituto
        regra.bloqueios = bloqueios
        regra.somente_se_tiver = somente_se_tiver
        regra.converter_shopee = converter_shopee
        session.add(regra)
        session.commit()
    return RedirectResponse(url="/regras", status_code=303)

# --- AGENDAMENTOS ---

@app.get("/agendamentos", response_class=HTMLResponse)
async def listar_agendamentos(request: Request, session: Session = Depends(get_session)):
    agendamentos = session.exec(select(Agendamento)).all()
    bots = session.exec(select(Bot)).all()
    return templates.TemplateResponse("agendamentos.html", {"request": request, "agendamentos": agendamentos, "bots": bots})

@app.post("/agendamentos/criar")
async def criar_agendamento(
    nome: str = Form(...), origem: str = Form(...), destino: str = Form(...),
    msg_id_atual: int = Form(...), tipo_envio: str = Form(...), horario: str = Form(...),
    bot_id: int = Form(...), 
    filtro: str = Form(None), substituto: str = Form(None), 
    bloqueios: str = Form(None), somente_se_tiver: str = Form(None),
    session: Session = Depends(get_session)
):
    novo = Agendamento(
        nome=nome, origem=origem, destino=destino, msg_id_atual=msg_id_atual,
        tipo_envio=tipo_envio, horario=horario, bot_id=bot_id, 
        filtro=filtro, substituto=substituto, bloqueios=bloqueios,
        somente_se_tiver=somente_se_tiver, ativo=True
    )
    session.add(novo); session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

@app.get("/agendamentos/deletar/{id}")
async def deletar_agendamento(id: int, session: Session = Depends(get_session)):
    item = session.get(Agendamento, id)
    if item: session.delete(item); session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

@app.get("/agendamentos/toggle/{id}")
async def toggle_agendamento(id: int, session: Session = Depends(get_session)):
    item = session.get(Agendamento, id)
    if item:
        item.ativo = not item.ativo
        session.add(item)
        session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

# --- BLOQUEIOS ---

@app.get("/bloqueios", response_class=HTMLResponse)
async def listar_bloqueios(request: Request):
    # Redireciona para regras, pois movemos os bloqueios para lá
    return RedirectResponse(url="/regras") 

# --- HTMX ---

@app.get("/htmx/logs", response_class=HTMLResponse)
async def pegar_logs_htmx(request: Request, session: Session = Depends(get_session)):
    logs = session.exec(select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)).all()
    return templates.TemplateResponse("fragmento_logs.html", {"request": request, "logs": logs})