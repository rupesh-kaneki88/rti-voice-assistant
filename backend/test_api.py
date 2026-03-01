"""
Test script for RTI Voice Assistant API
Run after starting server: python test_api.py
"""
import requests
import base64
import json

BASE_URL = "http://localhost:8000"


def test_health():
    print("\n=== Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200


def test_create_session():
    print("\n=== Create Session ===")
    response = requests.post(
        f"{BASE_URL}/session/create",
        json={"language": "hi"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    assert response.status_code == 200
    return data["session_id"]


def test_transcribe(session_id):
    print("\n=== Transcribe Audio ===")
    mock_audio = base64.b64encode(b"test audio").decode('utf-8')
    
    response = requests.post(
        f"{BASE_URL}/voice/transcribe",
        json={
            "audio": mock_audio,
            "language": "hi"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def test_update_form(session_id):
    print("\n=== Update Form ===")
    response = requests.post(
        f"{BASE_URL}/form/{session_id}/update",
        json={
            "field": "applicant_name",
            "value": "Test User"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200


def test_get_form(session_id):
    print("\n=== Get Form ===")
    response = requests.get(f"{BASE_URL}/form/{session_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200


def test_generate_document(session_id):
    print("\n=== Generate Document ===")
    response = requests.post(f"{BASE_URL}/form/{session_id}/generate")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200


def test_guidance():
    print("\n=== Get RTI Guidance ===")
    response = requests.post(
        f"{BASE_URL}/guidance/explain",
        params={"language": "hi"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    assert response.status_code == 200


def test_tts():
    print("\n=== Text to Speech ===")
    response = requests.post(
        f"{BASE_URL}/voice/tts",
        json={
            "text": "नमस्ते",
            "language": "hi"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200


def run_all_tests():
    print("=" * 60)
    print("RTI Voice Assistant API - Test Suite")
    print("=" * 60)
    
    try:
        test_health()
        session_id = test_create_session()
        test_transcribe(session_id)
        test_update_form(session_id)
        test_get_form(session_id)
        test_generate_document(session_id)
        test_guidance()
        test_tts()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to server.")
        print("Start the server with: uvicorn app:app --reload")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    run_all_tests()
