from sqlmodel import Session, select
from database import engine, Bot

def restaurar_dados():
    # Dados do Bot (Edite a session_string com a string REAL gerada pelo Telethon)
    bot_data = Bot(
        nome="API1",
        api_id="21993165",
        api_hash="2017110c1ffe36db9adc12f808cc09bc",
        phone="5511965396092",
        bot_token=None,
        tipo="user",
        # IMPORTANTE: Esta string abaixo deve ser a sessão válida longa gerada pelo Telethon.
        # Se você usar o api_hash aqui, o worker.py vai falhar ao conectar.
        session_string="1AZWarzQBu7nq-_Jb7w8-gl5ucJAoUATpQDe7vzTDPtOjFLtce3poFVNVSPLArKIb__7d7pHxLA5Bvgx6D_CmyL1HOyTFRN_rexBvVPulcU2e9m-gOOu-39SVhuo3ObI5-e-QaM_-niKKjutBkM6TkOB9ORe79PhvAebSKSkW4QVpsIKBRx32DAhNfWPQcY26OduaOhwxl3bunS-ylIGdFS4CC83dbXT5HAXEYA7UpLWAa6jRuh0KDndSP_kqNDsPme6T5disZkSnUkm6cF8j6VwbV1aQkseAbCB11eMreKsad-gI7VrV2FQTevvjlQg92qgQ-G4561lPWQERsO9_MtBEqxrqQ6E=", 
        ativo=True
    )

    with Session(engine) as session:
        # Verifica se já existe para não duplicar
        existente = session.exec(select(Bot).where(Bot.api_id == bot_data.api_id)).first()
        
        if existente:
            print(f"⚠️ O bot '{existente.nome}' já existe no banco.")
        else:
            session.add(bot_data)
            session.commit()
            print("✅ Bot 'TesteBot' inserido com sucesso!")

if __name__ == "__main__":
    restaurar_dados()