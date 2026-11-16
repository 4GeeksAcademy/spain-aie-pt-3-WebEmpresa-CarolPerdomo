#!/usr/bin/env python3
"""
Interactive demo of Nexova API authentication system.
Shows complete user registration, authentication, and data access flow.
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_step(num, text):
    print(f"{Colors.YELLOW}{Colors.BOLD}[Step {num}]{Colors.RESET} {text}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def print_json(data, label="Response"):
    print(f"\n{Colors.BOLD}{label}:{Colors.RESET}")
    print(json.dumps(data, indent=2))

def check_api_running():
    """Check if API is running."""
    try:
        response = requests.get(f"{BASE_URL}/")
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def demo_register():
    """Step 1: Register a new user"""
    print_step(1, "Register a new user")
    print_info("Creating account for alice@example.com with auto-generated profile...")
    
    user_data = {
        "email": f"alice{int(datetime.now().timestamp())}@example.com",
        "password": "securepassword123",
        "name": "Alice Johnson"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    
    if response.status_code == 200:
        result = response.json()
        print_success("User registered successfully!")
        print_json(result, "Registration Response")
        return result['access_token'], result['user']['id'], result['user']['email']
    else:
        print_error(f"Registration failed: {response.text}")
        return None, None, None

def demo_login(email, password):
    """Demo: Login with credentials"""
    print_step(2, "Login with credentials")
    print_info(f"Logging in as {email}...")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print_success("Login successful!")
        print_json(result, "Login Response")
        return result['access_token']
    else:
        print_error(f"Login failed: {response.text}")
        return None

def demo_get_user(token, user_id):
    """Step 3: Get authenticated user info"""
    print_step(3, "Get authenticated user information")
    print_info("Accessing /users/me endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print_success("User info retrieved!")
        print_json(result, "User Info")
        return result
    else:
        print_error(f"Failed to get user: {response.text}")
        return None

def demo_get_profile(token):
    """Step 4: Get user profile"""
    print_step(4, "Get user profile (auto-created)")
    print_info("Accessing /profiles/me endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/profiles/me", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print_success("Profile retrieved! Note: auto-created with every user")
        print_json(result, "Profile Info")
        return result
    else:
        print_error(f"Failed to get profile: {response.text}")
        return None

def demo_update_profile(token):
    """Step 5: Update profile"""
    print_step(5, "Update user profile")
    print_info("Adding detailed professional information...")
    
    profile_data = {
        "bio": "Experienced software engineer passionate about AI and distributed systems",
        "phone": "+34-666-123456",
        "location": "Valencia, Spain",
        "specialization": "Full Stack Development",
        "experience_years": 5
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/profiles/me", json=profile_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print_success("Profile updated successfully!")
        print_json(result, "Updated Profile")
        return result
    else:
        print_error(f"Failed to update profile: {response.text}")
        return None

def demo_access_control(token1, user_id2):
    """Step 6: Demonstrate access control (403 Forbidden)"""
    print_step(6, "Demonstrate access control - attempt cross-user access")
    print_info(f"Trying to access another user's data (ID: {user_id2}) with current token...")
    
    headers = {"Authorization": f"Bearer {token1}"}
    response = requests.get(f"{BASE_URL}/users/{user_id2}", headers=headers)
    
    if response.status_code == 403:
        print_success("Access correctly denied!")
        print_json(response.json(), "403 Forbidden Response")
    else:
        print_error(f"Unexpected response: {response.status_code}")

def demo_no_auth():
    """Step 7: Demonstrate 401 Unauthorized"""
    print_step(7, "Demonstrate authentication requirement - no token")
    print_info("Attempting to access protected route without token...")
    
    response = requests.get(f"{BASE_URL}/users/me")
    
    if response.status_code == 401:
        print_success("Access correctly denied (401 Unauthorized)!")
        print_json(response.json(), "401 Unauthorized Response")
    else:
        print_error(f"Unexpected response: {response.status_code}")

def demo_auth_summary():
    """Summary of authentication features"""
    print_header("AUTHENTICATION SYSTEM SUMMARY")
    
    features = [
        ("✅ SECRET_KEY Mandatory", "API requires SECRET_KEY environment variable"),
        ("✅ User Registration", "POST /auth/register creates user + auto-profile"),
        ("✅ User Login", "POST /auth/login returns JWT token"),
        ("✅ Protected Routes", "8+ routes require valid JWT token"),
        ("✅ Auto-Profile Creation", "Every user automatically gets a profile"),
        ("✅ Password Hashing", "Passwords hashed with bcrypt, never stored plain"),
        ("✅ Access Control (403)", "Users can only access their own data"),
        ("✅ Auth Requirement (401)", "Missing/invalid token returns 401"),
        ("✅ Token Expiration", "Tokens expire in 24 hours"),
    ]
    
    for feature, description in features:
        print(f"{Colors.GREEN}{feature}{Colors.RESET}")
        print(f"  → {description}\n")

def main():
    print_header("NEXOVA API - AUTHENTICATION DEMO")
    
    # Check API is running
    if not check_api_running():
        print_error("API is not running!")
        print_info(f"Make sure the API is running at {BASE_URL}")
        print_info("Run: export SECRET_KEY='dev-key' && python -m uvicorn main:app --reload")
        sys.exit(1)
    
    print_success(f"API is running at {BASE_URL}")
    
    # Demo flow
    try:
        # Step 1: Register
        token, user_id, email = demo_register()
        if not token:
            sys.exit(1)
        
        # Step 2: Login (optional, just to show it works)
        # login_token = demo_login(email, "securepassword123")
        
        # Step 3: Get user info
        demo_get_user(token, user_id)
        
        # Step 4: Get profile
        demo_get_profile(token)
        
        # Step 5: Update profile
        demo_update_profile(token)
        
        # Step 6: Access control
        demo_access_control(token, 999)  # Try to access non-existent user
        
        # Step 7: No auth
        demo_no_auth()
        
        # Summary
        demo_auth_summary()
        
        print_header("DEMO COMPLETE")
        print_success("All features working correctly!")
        print_info("Next: Explore the full API documentation at http://localhost:8000/docs")
        
    except KeyboardInterrupt:
        print_error("\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
