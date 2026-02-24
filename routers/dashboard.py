from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from models import Bot, LogExecucao, Configuracao
from core.config import templates
from core.deps import get_session

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
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

@router.get("/htmx/logs", response_class=HTMLResponse)
async def pegar_logs_htmx(request: Request, session: Session = Depends(get_session)):
    logs = session.exec(select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)).all()
    return templates.TemplateResponse("fragmento_logs.html", {"request": request, "logs": logs})
