import os
from sqlmodel import SQLModel, create_engine

# Permite configurar o caminho do banco via variável de ambiente (útil para Docker)
sqlite_file_name = os.getenv("DATABASE_URL", "database.db")

# Garante que a pasta do banco existe (caso o caminho tenha subpastas)
db_dir = os.path.dirname(sqlite_file_name)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    # Importar todos os modelos aqui para que o SQLModel os registre
    import models.config
    import models.bot
    import models.rule
    import models.schedule
    import models.log
    SQLModel.metadata.create_all(engine)
