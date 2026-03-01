"""
Test script for local Voice Service
Run after starting the server with: python test_local.py
"""
import requests
import base64
import json

# Configuration
BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed")


def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ Root endpoint passed")


def test_transcribe_english():
    """Test transcription with English"""
    print("\n=== Testing English Transcription ===")
    
    # Create mock audio data
    mock_audio = b"fake audio data for testing"
    audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
    
    payload = {
        "audio": audio_base64,
        "language": "en"
    }
    
    response = requests.post(f"{BASE_URL}/voice/transcribe", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['language'] == 'en'
    assert data['confidence'] == 0.95
    assert 'text' in data
    print("✓ English transcription passed")


def test_transcribe_hindi():
    """Test transcription with Hindi"""
    print("\n=== Testing Hindi Transcription ===")
    
    mock_audio = b"fake audio data for testing"
    audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
    
    payload = {
        "audio": audio_base64,
        "language": "hi"
    }
    
    response = requests.post(f"{BASE_URL}/voice/transcribe", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['language'] == 'hi'
    assert data['confidence'] == 0.95
    print("✓ Hindi transcription passed")


def test_transcribe_kannada():
    """Test transcription with Kannada"""
    print("\n=== Testing Kannada Transcription ===")
    
    mock_audio = b"fake audio data for testing"
    audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
    
    payload = {
        "audio": audio_base64,
        "language": "kn"
    }
    
    response = requests.post(f"{BASE_URL}/voice/transcribe", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['language'] == 'kn'
    assert data['confidence'] == 0.95
    print("✓ Kannada transcription passed")


def test_invalid_language():
    """Test with invalid language"""
    print("\n=== Testing Invalid Language ===")
    
    mock_audio = b"fake audio data"
    audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
    
    payload = {
        "audio": audio_base64,
        "language": "fr"  # French - not supported
    }
    
    response = requests.post(f"{BASE_URL}/voice/transcribe", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 400
    print("✓ Invalid language handling passed")


def test_invalid_audio():
    """Test with invalid base64 audio"""
    print("\n=== Testing Invalid Audio ===")
    
    payload = {
        "audio": "not-valid-base64!!!",
        "language": "en"
    }
    
    response = requests.post(f"{BASE_URL}/voice/transcribe", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 400
    print("✓ Invalid audio handling passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("RTI Voice Service - Local Testing")
    print("=" * 60)
    
    try:
        test_health()
        test_root()
        test_transcribe_english()
        test_transcribe_hindi()
        test_transcribe_kannada()
        test_invalid_language()
        test_invalid_audio()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to server. Make sure it's running:")
        print("  uvicorn app_local:app --reload --port 8000")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    run_all_tests()
