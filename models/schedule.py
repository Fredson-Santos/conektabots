from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .bot import Bot

class Agendamento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str           
    origem: str         
    destino: str        
    msg_id_atual: int   
    tipo_envio: str     
    horario: str        
    # Filtros e Edições
    filtro: Optional[str] = None
    substituto: Optional[str] = None
    bloqueios: Optional[str] = None
    somente_se_tiver: Optional[str] = None
    filtro_midia: str = Field(default="todos")
    
    bot_id: int = Field(foreign_key="bot.id")
    bot: Optional["Bot"] = Relationship(back_populates="agendamentos")
    ativo: bool = Field(default=True)
