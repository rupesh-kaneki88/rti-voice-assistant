"""
Test the conversational RTI agent
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_conversation_flow():
    """Test a complete conversation flow"""
    
    print("=" * 60)
    print("Testing RTI Conversational Agent")
    print("=" * 60)
    
    # 1. Create session
    print("\n1. Creating session...")
    response = requests.post(f"{BASE_URL}/session/create", json={"language": "en"})
    session = response.json()
    session_id = session['session_id']
    print(f"✓ Session created: {session_id}")
    
    # 2. Get initial greeting
    print("\n2. Getting initial greeting...")
    response = requests.post(
        f"{BASE_URL}/session/{session_id}/conversation",
        json={"message": "", "language": "en"}
    )
    result = response.json()
    print(f"Agent: {result['agent_response']}")
    
    # 3. User provides information request
    print("\n3. User: I want to know about government spending on education")
    response = requests.post(
        f"{BASE_URL}/session/{session_id}/conversation",
        json={
            "message": "I want to know about government spending on education",
            "language": "en"
        }
    )
    result = response.json()
    print(f"Agent: {result['agent_response']}")
    print(f"Form updates: {result['form_updates']}")
    
    # 4. User provides department
    print("\n4. User: Ministry of Education")
    response = requests.post(
        f"{BASE_URL}/session/{session_id}/conversation",
        json={
            "message": "Ministry of Education",
            "language": "en"
        }
    )
    result = response.json()
    print(f"Agent: {result['agent_response']}")
    print(f"Form updates: {result['form_updates']}")
    
    # 5. User provides name
    print("\n5. User: My name is Rajesh Kumar")
    response = requests.post(
        f"{BASE_URL}/session/{session_id}/conversation",
        json={
            "message": "My name is Rajesh Kumar",
            "language": "en"
        }
    )
    result = response.json()
    print(f"Agent: {result['agent_response']}")
    
    # 6. Check form data
    print("\n6. Checking form data...")
    response = requests.get(f"{BASE_URL}/form/{session_id}")
    form_data = response.json()
    print(f"Form data: {json.dumps(form_data['form_data'], indent=2)}")
    
    print("\n" + "=" * 60)
    print("✓ Conversation test completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_conversation_flow()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
