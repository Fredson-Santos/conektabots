import os
from sqlmodel import SQLModel, create_engine

# URL de conexão com PostgreSQL via variável de ambiente
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://conekta:conekta@localhost:5432/conektabots"
)

engine = create_engine(database_url)

def create_db_and_tables():
    # Importar todos os modelos aqui para que o SQLModel os registre
    import app.models.config
    import app.models.bot
    import app.models.rule
    import app.models.schedule
    import app.models.log
    SQLModel.metadata.create_all(engine)
