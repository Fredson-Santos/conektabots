from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlmodel import Session, select
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from app.models import Bot
from app.core.config import templates, TEMP_CLIENTS
from app.core.deps import get_session

router = APIRouter(prefix="/bots", tags=["bots"])

@router.get("/adicionar", response_class=HTMLResponse)
async def form_adicionar_bot(request: Request):
    return templates.TemplateResponse("adicionar_bot.html", {"request": request})

@router.post("/criar")
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
    sessao_final = session_string
    if tipo == "bot" and not session_string:
        sessao_final = None 
    
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

@router.get("/deletar/{id}")
async def deletar_bot(id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)
    if bot:
        session.delete(bot)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

@router.get("/toggle/{id}")
async def toggle_bot(id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)
    if bot:
        bot.ativo = not bot.ativo
        session.add(bot)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

@router.get("/editar/{id}", response_class=HTMLResponse)
async def form_editar_bot(request: Request, id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)
    if not bot:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("editar_bot.html", {"request": request, "bot": bot})

@router.post("/editar/{id}")
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
        
        if session_string and session_string.strip():
            bot.session_string = session_string
            
        session.add(bot)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

# --- LOGIN USERBOT ---

@router.post("/userbot/enviar-codigo", response_class=HTMLResponse)
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

@router.post("/userbot/validar-codigo", response_class=HTMLResponse)
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

@router.post("/userbot/validar-senha")
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
