from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .rule import Regra
    from .schedule import Agendamento

class Bot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    api_id: str
    api_hash: str
    phone: Optional[str] = None
    bot_token: Optional[str] = None
    tipo: str = Field(default="user")
    session_string: Optional[str] = None
    ativo: bool = Field(default=True)
    
    regras: List["Regra"] = Relationship(back_populates="bot", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    agendamentos: List["Agendamento"] = Relationship(back_populates="bot", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
