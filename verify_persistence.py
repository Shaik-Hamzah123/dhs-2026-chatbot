import requests
import json

def test_chat_persistence():
    url = "http://127.0.0.1:8000/chat"
    
    # 1. First interaction: Introduce name
    payload1 = {
        "user_input": "Hello, my name is Hamzah.",
        "mem0_user_id": "test_user_123",
        "mem0_session_id": "test_session_456",
        "signed_in": True,
        "messages": []
    }
    
    print("Sending message 1...")
    response1 = requests.post(url, json=payload1)
    print(f"Response 1: {response1.text}")
    
    # 2. Second interaction: Ask about the name
    # We simulate what the frontend does: appending the previous user-assistant turn
    payload2 = {
        "user_input": "What is my name?",
        "mem0_user_id": "test_user_123",
        "mem0_session_id": "test_session_456",
        "signed_in": True,
        "messages": [
            {"role": "user", "content": "Hello, my name is Hamzah."},
            {"role": "assistant", "content": response1.text}
        ]
    }
    
    print("\nSending message 2 (with history)...")
    response2 = requests.post(url, json=payload2)
    print(f"Response 2: {response2.text}")
    
    if "Hamzah" in response2.text:
        print("\n✅ SUCCESS: The bot remembered the name from the history!")
    else:
        print("\n❌ FAILURE: The bot did not remember the name.")

if __name__ == "__main__":
    try:
        test_chat_persistence()
    except Exception as e:
        print(f"Error: {e}")
