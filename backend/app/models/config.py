from typing import Optional
from sqlmodel import Field, SQLModel

class Configuracao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shopee_app_id: Optional[str] = None
    shopee_app_secret: Optional[str] = None
