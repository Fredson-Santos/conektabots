#!/usr/bin/env python3
"""
ConektaBots Backend Validation Script
Tests all critical endpoints for Task A2 validation
"""

import json
import httpx
import asyncio
from pathlib import Path
import time


class EndpointValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.tests_passed = 0
        self.tests_failed = 0
        self.tokens = {}
        self.client = httpx.Client()
        self.test_results = []
    
    def log_test(self, name, status, details=""):
        """Log test result"""
        status_str = "✓" if status else "✗"
        status_color = "\033[92m" if status else "\033[91m"
        reset_color = "\033[0m"
        
        print(f"  {status_color}{status_str}{reset_color} {name}")
        if details:
            print(f"    {details}")
        
        if status:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        self.test_results.append({
            "test": name,
            "status": "PASS" if status else "FAIL",
            "details": details
        })
    
    def test_endpoint(self, method, path, **kwargs):
        """Generic endpoint tester"""
        try:
            url = f"{self.base_url}{path}"
            response = self.client.request(method, url, timeout=10, **kwargs)
            return response
        except Exception as e:
            print(f"      ERROR: {e}")
            return None
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("\n" + "="*70)
        print("ConektaBots Backend Validation".center(70))
        print("="*70)
        
        # A. Health Check
        print("\n[A] Health Check (No Auth Required)")
        resp = self.test_endpoint("GET", "/health")
        if resp and resp.status_code == 200:
            data = resp.json()
            self.log_test("GET /health", True, f"Status: {resp.status_code}, DB: {data.get('database')}")
        else:
            self.log_test("GET /health", False, f"Status: {resp.status_code if resp else 'N/A'}")
        
        # B. Register (create test user)
        print("\n[B] Register - Create Test Account")
        register_data = {
            "email": f"testuser-{int(time.time())}@example.com",
            "password": "Test123!@",
            "password_confirm": "Test123!@",
            "first_name": "Test",
            "last_name": "User"
        }
        resp = self.test_endpoint("POST", "/api/v1/auth/register", json=register_data)
        if resp and resp.status_code == 201:
            self.tokens = resp.json()
            self.log_test(
                "POST /api/v1/auth/register",
                True,
                f"Status: 201, User ID: {self.tokens.get('user_id')}, TTL: {self.tokens.get('expires_in')}s"
            )
        else:
            self.log_test("POST /api/v1/auth/register", False, f"Status: {resp.status_code if resp else 'N/A'}")
            return  # Can't continue without tokens
        
        # C. Login
        print("\n[C] Login - With Created Account")
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        resp = self.test_endpoint("POST", "/api/v1/auth/login", json=login_data)
        if resp and resp.status_code == 200:
            login_response = resp.json()
            self.log_test(
                "POST /api/v1/auth/login",
                True,
                f"Status: 200, Token Type: {login_response.get('token_type')}"
            )
        else:
            self.log_test("POST /api/v1/auth/login", False, f"Status: {resp.status_code if resp else 'N/A'}")
        
        # D. Get Bots (Protected Endpoint)
        print("\n[D] Get Bots - Protected Endpoint with Valid Token")
        headers = {"Authorization": f"Bearer {self.tokens.get('access_token')}"}
        resp = self.test_endpoint("GET", "/api/v1/bots", headers=headers)
        if resp and resp.status_code == 200:
            data = resp.json()
            self.log_test(
                "GET /api/v1/bots (with token)",
                True,
                f"Status: 200, Total: {data.get('total', 'N/A')}, Page: {data.get('page', 'N/A')}"
            )
        else:
            self.log_test("GET /api/v1/bots (with token)", False, f"Status: {resp.status_code if resp else 'N/A'}")
        
        # E. Token Refresh
        print("\n[E] Token Refresh - Generate New Access Token")
        refresh_data = {"refresh_token": self.tokens.get('refresh_token')}
        resp = self.test_endpoint("POST", "/api/v1/auth/refresh", json=refresh_data)
        if resp and resp.status_code == 200:
            refresh_response = resp.json()
            self.log_test(
                "POST /api/v1/auth/refresh",
                True,
                f"Status: 200, New Token: {refresh_response.get('access_token', 'N/A')[:30]}..."
            )
        else:
            self.log_test("POST /api/v1/auth/refresh", False, f"Status: {resp.status_code if resp else 'N/A'}")
        
        # F. Get Marketplaces
        print("\n[F] Get Marketplaces - Protected Endpoint")
        resp = self.test_endpoint("GET", "/api/v1/marketplaces", headers=headers)
        if resp and resp.status_code == 200:
            self.log_test("GET /api/v1/marketplaces", True, f"Status: 200")
        else:
            self.log_test("GET /api/v1/marketplaces", False, f"Status: {resp.status_code if resp else 'N/A'}")
        
        # G. Error Case - Invalid Token
        print("\n[G] Error Handling - Invalid Token (Expect 401)")
        bad_headers = {"Authorization": "Bearer invalid-token-xyz"}
        resp = self.test_endpoint("GET", "/api/v1/bots", headers=bad_headers)
        if resp and resp.status_code == 401:
            self.log_test("GET /api/v1/bots (invalid token)", True, "Status: 401 (Unauthorized)")
        else:
            self.log_test("GET /api/v1/bots (invalid token)", False, f"Status: {resp.status_code if resp else 'N/A'} (expected 401)")
        
        # H. Error Case - Missing Auth Header
        print("\n[H] Error Handling - Missing Auth Header (Expect 403)")
        resp = self.test_endpoint("GET", "/api/v1/bots")
        if resp and resp.status_code == 403:
            self.log_test("GET /api/v1/bots (no auth)", True, "Status: 403 (Forbidden)")
        else:
            self.log_test("GET /api/v1/bots (no auth)", False, f"Status: {resp.status_code if resp else 'N/A'} (expected 403)")
        
        # Summary
        print("\n" + "="*70)
        print("VALIDATION SUMMARY".center(70))
        print("="*70)
        print(f"\nTests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Total Tests:  {self.tests_passed + self.tests_failed}")
        
        if self.tests_failed == 0:
            print(f"\n✓ All {self.tests_passed} tests passed! Backend is ready for frontend integration.")
        else:
            print(f"\n✗ {self.tests_failed} test(s) failed. Check errors above.")
        
        print("="*70 + "\n")
        
        return self.tests_failed == 0


if __name__ == "__main__":
    validator = EndpointValidator()
    success = validator.run_all_tests()
    
    # Save results to file for documentation
    results_file = Path("c:/Users/Fred/Projetos/conektabots/.project/task-a2-validation-results.json")
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests_passed": validator.tests_passed,
            "tests_failed": validator.tests_failed,
            "results": validator.test_results
        }, f, indent=2)
    
    exit(0 if success else 1)
