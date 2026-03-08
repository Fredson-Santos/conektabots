from fastapi import FastAPI
from app.routers import dashboard, bots, rules, schedules, settings

app = FastAPI(title="ConektaBots API")

# Registro de Roteadores
app.include_router(dashboard.router)
app.include_router(bots.router)
app.include_router(rules.router)
app.include_router(schedules.router)
app.include_router(settings.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
