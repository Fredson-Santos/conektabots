import httpx
import asyncio
import json

async def test_register():
    async with httpx.AsyncClient() as client:
        payload = {
            "email": "test@example.com",
            "password": "Test123456",
            "password_confirm": "Test123456",
            "first_name": "João",
            "last_name": "Silva"
        }
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/register",
                json=payload,
                timeout=5.0
            )
            print(f"Status: {response.status_code}")
            try:
                data = response.json()
                print(json.dumps(data, indent=2))
            except:
                print(f"Response: {response.text}")
                
            if response.status_code == 201:
                print(f"\n✓ Success! User registered.")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

asyncio.run(test_register())

