import requests
import json
import time

# API base URL
API_BASE = "http://localhost:8001/api"

def test_complete_flow():
    print("=== Testing Complete Zeny AI Flow with Authentication ===")
    
    # Step 1: Login as admin
    print("1. Logging in as admin...")
    login_data = {"username": "newadmin", "password": "newpass123"}
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    if response.status_code != 200:
        # Try with original credentials
        login_data = {"username": "admin", "password": "admin"}
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token_data = response.json()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    print(f"✅ Logged in as: {token_data['user']['username']}")
    
    # Step 2: Create an avatar
    print("\n2. Creating avatar...")
    avatar_data = {
        "name": "SummaryBot",
        "personality": "Helpful and detailed",
        "description": "A bot that provides detailed conversations for summary testing"
    }
    
    response = requests.post(f"{API_BASE}/avatars", json=avatar_data, headers=headers)
    if response.status_code != 200:
        print(f"Avatar creation failed: {response.text}")
        return
    
    avatar = response.json()
    avatar_id = avatar['id']
    print(f"✅ Created avatar: {avatar['name']} (ID: {avatar_id})")
    
    # Step 3: Start a conversation
    print("\n3. Starting conversation...")
    conv_data = {
        "avatar_id": avatar_id,
        "participant_name": "Alice Johnson"
    }
    
    response = requests.post(f"{API_BASE}/conversations", json=conv_data)
    if response.status_code != 200:
        print(f"Conversation creation failed: {response.text}")
        return
    
    conversation = response.json()
    conversation_id = conversation['id']
    print(f"✅ Started conversation: {conversation_id}")
    
    # Step 4: Send multiple messages
    print("\n4. Sending messages...")
    messages = [
        "Hello SummaryBot! I'm having trouble with my project management.",
        "I have three major projects running simultaneously and I'm losing track of deadlines.",
        "Can you help me organize my workflow better?",
        "What tools would you recommend for better task tracking?",
        "Also, how can I prioritize tasks when everything seems urgent?"
    ]
    
    for i, msg in enumerate(messages):
        message_data = {
            "sender": "Alice Johnson",
            "content": msg
        }
        
        response = requests.post(f"{API_BASE}/conversations/{conversation_id}/messages", json=message_data)
        if response.status_code == 200:
            print(f"✅ Sent message {i+1}: {msg[:50]}...")
        else:
            print(f"❌ Failed to send message {i+1}")
        
        time.sleep(0.5)  # Small delay between messages
    
    # Step 5: Get conversation to see all messages
    print("\n5. Retrieving conversation...")
    response = requests.get(f"{API_BASE}/conversations/{conversation_id}")
    if response.status_code == 200:
        conv = response.json()
        print(f"✅ Conversation has {len(conv['messages'])} messages")
    
    # Step 6: Generate summary
    print("\n6. Generating summary...")
    response = requests.post(f"{API_BASE}/conversations/{conversation_id}/summary")
    if response.status_code != 200:
        print(f"Summary generation failed: {response.text}")
        return
    
    summary = response.json()
    print(f"✅ Generated summary:")
    print(f"Summary ID: {summary['id']}")
    print(f"Summary Text: {summary['summary_text']}")
    print(f"Key Points:")
    for point in summary['key_points']:
        print(f"  • {point}")
    
    # Step 7: Get all summaries for user
    print("\n7. Getting all summaries for user...")
    response = requests.get(f"{API_BASE}/summaries", headers=headers)
    if response.status_code == 200:
        summaries = response.json()
        print(f"✅ Found {len(summaries)} summaries for current user")
        for summ in summaries:
            print(f"  - Summary {summ['id'][-8:]}: {summ['summary_text'][:60]}...")
    else:
        print(f"Failed to get summaries: {response.text}")
    
    # Step 8: Get summaries for specific avatar
    print(f"\n8. Getting summaries for avatar {avatar_id}...")
    response = requests.get(f"{API_BASE}/avatars/{avatar_id}/summaries", headers=headers)
    if response.status_code == 200:
        avatar_summaries = response.json()
        print(f"✅ Found {len(avatar_summaries)} summaries for this avatar")
    else:
        print(f"Failed to get avatar summaries: {response.text}")
    
    print("\n🎉 Complete flow test successful!")
    return True

if __name__ == "__main__":
    try:
        test_complete_flow()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")