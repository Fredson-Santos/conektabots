from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlmodel import Session, select
from models import Bot, Regra
from core.config import templates
from core.deps import get_session

router = APIRouter(prefix="/regras", tags=["regras"])

@router.get("", response_class=HTMLResponse)
async def listar_regras(request: Request, session: Session = Depends(get_session)):
    regras = session.exec(select(Regra)).all()
    bots = session.exec(select(Bot)).all()
    return templates.TemplateResponse("regras.html", {"request": request, "regras": regras, "bots": bots})

@router.post("/criar")
async def criar_regra(
    nome: str = Form(...), origem: str = Form(...), destino: str = Form(...), bot_id: int = Form(...),
    filtro: str = Form(None), substituto: str = Form(None), bloqueios: str = Form(None), somente_se_tiver: str = Form(None),
    filtro_midia: str = Form("todos"),
    converter_shopee: bool = Form(False),
    session: Session = Depends(get_session)
):
    nova_regra = Regra(
        nome=nome, origem=origem, destino=destino, bot_id=bot_id,
        filtro=filtro, substituto=substituto, bloqueios=bloqueios, somente_se_tiver=somente_se_tiver, 
        filtro_midia=filtro_midia, converter_shopee=converter_shopee, ativo=True
    )
    session.add(nova_regra)
    session.commit()
    return RedirectResponse(url="/regras", status_code=303)

@router.get("/toggle/{id}")
async def toggle_regra(id: int, session: Session = Depends(get_session)):
    regra = session.get(Regra, id)
    if regra:
        regra.ativo = not regra.ativo
        session.add(regra)
        session.commit()
    return RedirectResponse(url="/regras", status_code=303)

@router.get("/deletar/{id}")
async def deletar_regra(id: int, session: Session = Depends(get_session)):
    regra = session.get(Regra, id)
    if regra: session.delete(regra); session.commit()
    return RedirectResponse(url="/regras", status_code=303)

@router.get("/editar/{id}", response_class=HTMLResponse)
async def form_editar_regra(request: Request, id: int, session: Session = Depends(get_session)):
    regra = session.get(Regra, id)
    bots = session.exec(select(Bot)).all()
    if not regra:
        return RedirectResponse(url="/regras", status_code=303)
    return templates.TemplateResponse("editar_regra.html", {"request": request, "regra": regra, "bots": bots})

@router.post("/editar/{id}")
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
    filtro_midia: str = Form("todos"),
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
        regra.filtro_midia = filtro_midia
        regra.converter_shopee = converter_shopee
        session.add(regra)
        session.commit()
    return RedirectResponse(url="/regras", status_code=303)
