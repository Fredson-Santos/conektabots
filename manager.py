import asyncio
from sqlmodel import Session, select
from app.core.database import engine
from app.models import Bot
from worker import BotWorker

async def main():
    print("🚀 INICIANDO SISTEMA CONEKTA BOTS...")
    
    # 1. Buscar bots ativos no banco
    workers = []
    with Session(engine) as session:
        statement = select(Bot).where(Bot.ativo == True)
        bots_ativos = session.exec(statement).all()
        
        if not bots_ativos:
            print("⚠️ Nenhum bot ativo encontrado no banco de dados.")
            return

        print(f"📋 Encontrados {len(bots_ativos)} bots para iniciar.")

        # 2. Criar instâncias dos Workers
        for bot_dados in bots_ativos:
            worker = BotWorker(bot_dados)
            workers.append(worker)

    # 3. Rodar todos simultaneamente
    # asyncio.gather faz todos rodarem em paralelo (multitarefa)
    tarefas = [worker.start() for worker in workers]
    
    try:
        await asyncio.gather(*tarefas)
    except KeyboardInterrupt:
        print("\n🛑 Parando o sistema...")
        for worker in workers:
            await worker.stop()
        print("Sistema desligado.")

if __name__ == "__main__":
    asyncio.run(main())