import httpx
import asyncio
import json

async def test_full_auth_flow():
    """Test complete authentication flow: register -> login -> refresh token -> protected endpoint."""
    
    print("=" * 60)
    print("[TEST] TESTING CONEKTABOTS API - FULL AUTH FLOW")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Register user
        print("\n[1] Testing Registration...")
        register_payload = {
            "email": "fulltest@example.com",
            "password": "SecurePassword123",
            "password_confirm": "SecurePassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/register",
                json=register_payload,
                timeout=5.0
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                access_token = data.get("access_token")
                refresh_token = data.get("refresh_token")
                user_id = data.get("user_id")
                tenant_id = data.get("tenant_id")
                print(f"   [OK] Registration successful")
                print(f"      - User ID: {user_id}")
                print(f"      - Tenant ID: {tenant_id}")
            else:
                print(f"   [FAIL] Registration failed: {response.json()}")
                return
                
        except Exception as e:
            print(f"   [ERROR] {type(e).__name__}: {e}")
            return
        
        # Test 2: Login
        print("\n[2] Testing Login...")
        login_payload = {
            "email": "fulltest@example.com",
            "password": "SecurePassword123"
        }
        
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/login",
                json=login_payload,
                timeout=5.0
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   [OK] Login successful")
                print(f"      - Token Type: {data.get('token_type')}")
                access_token = data.get("access_token")
            else:
                print(f"   [FAIL] Login failed: {response.json()}")
                return
                
        except Exception as e:
            print(f"   [ERROR] {type(e).__name__}: {e}")
            return
        
        # Test 3: Protected endpoint (get tenants)
        print("\n[3] Testing Protected Endpoint (GET /api/v1/tenants)...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = await client.get(
                "http://localhost:8000/api/v1/tenants",
                headers=headers,
                timeout=5.0
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   [OK] Protected endpoint accessible")
                print(f"      - Response: {json.dumps(data, indent=8)}")
            else:
                print(f"   [FAIL] Protected endpoint failed: {response.json()}")
                
        except Exception as e:
            print(f"   [ERROR] {type(e).__name__}: {e}")
        
        # Test 4: Refresh token
        print("\n[4] Testing Token Refresh...")
        refresh_payload = {"refresh_token": refresh_token}
        
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/refresh",
                json=refresh_payload,
                timeout=5.0
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   [OK] Token refresh successful")
                print(f"      - New Access Token: {data.get('access_token')[:50]}...")
            else:
                print(f"   [FAIL] Token refresh failed: {response.json()}")
                
        except Exception as e:
            print(f"   [ERROR] {type(e).__name__}: {e}")
        
        # Test 5: Health check
        print("\n[5] Testing Health Check...")
        try:
            response = await client.get(
                "http://localhost:8000/healthz",
                timeout=5.0
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   [OK] API is healthy")
                print(f"      - Status: {data.get('status')}")
            else:
                print(f"   [FAIL] Health check failed: {response.text}")
                
        except Exception as e:
            print(f"   [ERROR] {type(e).__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("[COMPLETE] TEST SUITE FINISHED")
    print("=" * 60)

asyncio.run(test_full_auth_flow())
