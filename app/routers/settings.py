from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlmodel import Session, select
from app.models import Configuracao
from app.core.config import templates
from app.core.deps import get_session

router = APIRouter(prefix="/configuracoes", tags=["configuracoes"])

@router.get("", response_class=HTMLResponse)
async def ver_configuracoes(request: Request, session: Session = Depends(get_session)):
    config = session.exec(select(Configuracao)).first()
    return templates.TemplateResponse("configuracoes.html", {"request": request, "config": config})

@router.post("/salvar")
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

@router.get("/bloqueios")
async def listar_bloqueios():
    # Redireciona para regras, pois movemos os bloqueios para lá
    return RedirectResponse(url="/regras")
