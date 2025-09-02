import requests
import json

# API base URL
API_BASE = "http://localhost:8001/api"

def test_authentication():
    print("=== Testing Authentication System ===")
    
    # Test admin login
    print("1. Testing admin login...")
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    print(f"Admin Login Response: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print(f"Login successful! User: {token_data['user']['username']}")
        print(f"Is Admin: {token_data['user']['is_admin']}")
        access_token = token_data['access_token']
        headers = {"Authorization": f"Bearer {access_token}"}
    else:
        print(f"Login failed: {response.text}")
        return None
    
    # Test getting current user
    print("\n2. Testing get current user...")
    response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    print(f"Get Current User Response: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"Current user: {user['username']} (Admin: {user['is_admin']})")
    
    # Test creating avatar with authentication
    print("\n3. Testing avatar creation with authentication...")
    avatar_data = {
        "name": "AuthTestBot",
        "personality": "Secure and authenticated",
        "description": "A test bot for authentication system"
    }
    
    response = requests.post(f"{API_BASE}/avatars", json=avatar_data, headers=headers)
    print(f"Create Avatar Response: {response.status_code}")
    if response.status_code == 200:
        avatar = response.json()
        print(f"Created avatar: {avatar['name']} (Owner: {avatar['owner_id']})")
    else:
        print(f"Error: {response.text}")
    
    # Test getting avatars with authentication
    print("\n4. Testing get avatars with authentication...")
    response = requests.get(f"{API_BASE}/avatars", headers=headers)
    print(f"Get Avatars Response: {response.status_code}")
    if response.status_code == 200:
        avatars = response.json()
        print(f"Found {len(avatars)} avatars for current user")
    
    # Test getting summaries with authentication
    print("\n5. Testing get summaries with authentication...")
    response = requests.get(f"{API_BASE}/summaries", headers=headers)
    print(f"Get Summaries Response: {response.status_code}")
    if response.status_code == 200:
        summaries = response.json()
        print(f"Found {len(summaries)} summaries for current user")
    
    # Test updating admin credentials
    print("\n6. Testing admin credentials update...")
    new_credentials = {
        "new_username": "newadmin",
        "new_password": "newpass123"
    }
    
    response = requests.put(f"{API_BASE}/auth/admin/credentials", json=new_credentials, headers=headers)
    print(f"Update Admin Credentials Response: {response.status_code}")
    if response.status_code == 200:
        print("Admin credentials updated successfully")
        
        # Test login with new credentials
        print("\n7. Testing login with new credentials...")
        new_login_data = {
            "username": "newadmin",
            "password": "newpass123"
        }
        response = requests.post(f"{API_BASE}/auth/login", json=new_login_data)
        print(f"New Admin Login Response: {response.status_code}")
        if response.status_code == 200:
            print("Login with new credentials successful!")
        else:
            print(f"Login with new credentials failed: {response.text}")
    else:
        print(f"Failed to update admin credentials: {response.text}")
    
    return headers

def test_user_registration():
    print("\n=== Testing User Registration ===")
    
    # Test user registration
    print("1. Testing user registration...")
    register_data = {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com"
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=register_data)
    print(f"User Registration Response: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"Registered user: {user['username']} (Admin: {user['is_admin']})")
        
        # Test login with new user
        print("\n2. Testing login with new user...")
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        print(f"User Login Response: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"User login successful! User: {token_data['user']['username']}")
        else:
            print(f"User login failed: {response.text}")
    else:
        print(f"Registration failed: {response.text}")

def main():
    print("Starting Authentication API Tests\n")
    
    try:
        # Test authentication system
        headers = test_authentication()
        
        # Test user registration
        test_user_registration()
        
        print("\n=== All Authentication Tests Completed! ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    main()