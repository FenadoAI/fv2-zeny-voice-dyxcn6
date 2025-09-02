import requests
import json
import time

# API base URL
API_BASE = "http://localhost:8001/api"

def test_avatars():
    print("=== Testing Avatar Management ===")
    
    # Test creating an avatar
    print("1. Creating avatar...")
    avatar_data = {
        "name": "ZenyBot",
        "personality": "Friendly and helpful",
        "description": "A friendly AI assistant that helps with daily tasks",
        "owner_id": "user-123"
    }
    
    response = requests.post(f"{API_BASE}/avatars", json=avatar_data)
    print(f"Create Avatar Response: {response.status_code}")
    if response.status_code == 200:
        avatar = response.json()
        print(f"Created avatar: {avatar['name']} (ID: {avatar['id']})")
        avatar_id = avatar['id']
    else:
        print(f"Error: {response.text}")
        return None
    
    # Test getting avatars
    print("\n2. Getting all avatars...")
    response = requests.get(f"{API_BASE}/avatars")
    print(f"Get Avatars Response: {response.status_code}")
    if response.status_code == 200:
        avatars = response.json()
        print(f"Found {len(avatars)} avatars")
        for av in avatars:
            print(f"  - {av['name']}: {av['description']}")
    
    return avatar_id

def test_conversations(avatar_id):
    print("\n=== Testing Conversation Management ===")
    
    # Test creating a conversation
    print("1. Creating conversation...")
    conv_data = {
        "avatar_id": avatar_id,
        "participant_name": "John Doe"
    }
    
    response = requests.post(f"{API_BASE}/conversations", json=conv_data)
    print(f"Create Conversation Response: {response.status_code}")
    if response.status_code == 200:
        conversation = response.json()
        print(f"Created conversation with {conversation['participant_name']} (ID: {conversation['id']})")
        conversation_id = conversation['id']
    else:
        print(f"Error: {response.text}")
        return None
    
    # Test sending messages
    print("\n2. Sending messages...")
    messages = [
        "Hello ZenyBot, how are you today?",
        "Can you help me with planning my day?",
        "What should I do first?"
    ]
    
    for msg in messages:
        message_data = {
            "sender": "John Doe",
            "content": msg
        }
        
        response = requests.post(f"{API_BASE}/conversations/{conversation_id}/messages", json=message_data)
        print(f"Send Message Response: {response.status_code}")
        if response.status_code == 200:
            print(f"  Sent: {msg}")
        
        # Wait a bit between messages
        time.sleep(1)
    
    # Test getting the conversation
    print("\n3. Getting conversation with messages...")
    response = requests.get(f"{API_BASE}/conversations/{conversation_id}")
    if response.status_code == 200:
        conv = response.json()
        print(f"Conversation has {len(conv['messages'])} messages:")
        for i, msg in enumerate(conv['messages']):
            print(f"  {i+1}. {msg['sender']}: {msg['content'][:100]}...")
    
    return conversation_id

def test_summaries(conversation_id):
    print("\n=== Testing Summary Generation ===")
    
    # Test generating summary
    print("1. Generating summary...")
    response = requests.post(f"{API_BASE}/conversations/{conversation_id}/summary")
    print(f"Generate Summary Response: {response.status_code}")
    if response.status_code == 200:
        summary = response.json()
        print(f"Generated summary (ID: {summary['id']})")
        print(f"Summary: {summary['summary_text']}")
        print("Key points:")
        for point in summary['key_points']:
            print(f"  - {point}")
        summary_id = summary['id']
    else:
        print(f"Error: {response.text}")
        return None
    
    # Test getting all summaries
    print("\n2. Getting all summaries...")
    response = requests.get(f"{API_BASE}/summaries")
    if response.status_code == 200:
        summaries = response.json()
        print(f"Found {len(summaries)} summaries")
        for summ in summaries:
            print(f"  - Summary {summ['id'][-8:]}: {summ['summary_text'][:50]}...")
    
    return summary_id

def main():
    print("Starting Zeny AI API Tests\n")
    
    try:
        # Test API root
        response = requests.get(f"{API_BASE}/")
        print(f"API Root Response: {response.status_code}")
        if response.status_code == 200:
            print(f"Message: {response.json()['message']}")
        
        # Test avatar management
        avatar_id = test_avatars()
        if not avatar_id:
            print("Avatar test failed, stopping...")
            return
        
        # Test conversation management
        conversation_id = test_conversations(avatar_id)
        if not conversation_id:
            print("Conversation test failed, stopping...")
            return
        
        # Test summary generation
        summary_id = test_summaries(conversation_id)
        if not summary_id:
            print("Summary test failed, stopping...")
            return
        
        print("\n=== All Tests Completed Successfully! ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    main()