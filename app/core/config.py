from fastapi.templating import Jinja2Templates

# Cache temporário de login
TEMP_CLIENTS = {}

# Inicializa o sistema de templates
templates = Jinja2Templates(directory="templates")
