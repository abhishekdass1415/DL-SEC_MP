#!/usr/bin/env python3
"""
Quick test script to verify the DL-SEC system is working properly.
"""

import requests
import time
import sys
import os

API_BASE_URL = "http://localhost:5000/api"

def test_backend_connection():
    """Test if backend is running"""
    print("🔍 Testing backend connection...")
    try:
        response = requests.get(f"{API_BASE_URL}/model/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running")
            print(f"   Model loaded: {data.get('model_loaded', False)}")
            print(f"   Scaler loaded: {data.get('scaler_loaded', False)}")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is the server running?")
        print("   Start the backend with: python backend/app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_dataset_load():
    """Test loading the test dataset"""
    print("\n📁 Testing dataset loading...")
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    test_dataset_path = os.path.join(project_root, "UNSW_NB15_testing-set.csv")
    
    # Convert to absolute path
    test_dataset_path = os.path.abspath(test_dataset_path)
    
    if not os.path.exists(test_dataset_path):
        print(f"⚠️  Test dataset not found at: {test_dataset_path}")
        print("   Please ensure UNSW_NB15_testing-set.csv is in the project root")
        return False
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dataset/load",
            json={"file_path": test_dataset_path},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dataset loaded successfully")
            print(f"   Total records: {data.get('total_records', 0)}")
            print(f"   Columns: {len(data.get('columns', []))}")
            return True
        else:
            print(f"❌ Failed to load dataset: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error loading dataset: {str(e)}")
        return False

def test_dataset_stats():
    """Test getting dataset statistics"""
    print("\n📊 Testing dataset statistics...")
    try:
        response = requests.get(f"{API_BASE_URL}/dataset/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"⚠️  {data['error']}")
                return False
            print(f"✅ Dataset statistics retrieved")
            print(f"   Total records: {data.get('total_records', 0)}")
            print(f"   Current index: {data.get('current_index', 0)}")
            print(f"   Remaining: {data.get('remaining_records', 0)}")
            if 'threats' in data:
                print(f"   Threats: {data.get('threats', 0)}")
                print(f"   Normal: {data.get('normal', 0)}")
            return True
        else:
            print(f"❌ Failed to get stats: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting stats: {str(e)}")
        return False

def test_threat_detection():
    """Test threat detection with a sample record"""
    print("\n🔍 Testing threat detection...")
    try:
        # Process a single record
        response = requests.post(
            f"{API_BASE_URL}/dataset/process",
            json={"batch_size": 1},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            prediction = data.get('prediction', {})
            print(f"✅ Threat detection test completed")
            print(f"   Threat detected: {prediction.get('is_threat', False)}")
            print(f"   Confidence: {prediction.get('confidence', 0):.2%}")
            print(f"   Threat type: {prediction.get('threat_type', 'Unknown')}")
            print(f"   Severity: {prediction.get('severity', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed to process record: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing threat detection: {str(e)}")
        return False

def test_streaming_status():
    """Test streaming status"""
    print("\n🔄 Testing streaming status...")
    try:
        response = requests.get(f"{API_BASE_URL}/dataset/stream/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Streaming status retrieved")
            print(f"   Streaming: {'Active' if data.get('is_running') else 'Stopped'}")
            print(f"   Interval: {data.get('interval', 0)}s")
            return True
        else:
            print(f"❌ Failed to get streaming status: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting streaming status: {str(e)}")
        return False

def test_threats_endpoint():
    """Test getting threats"""
    print("\n📋 Testing threats endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/threats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            threats_count = len(data.get('threats', []))
            print(f"✅ Threats endpoint working")
            print(f"   Threats found: {threats_count}")
            return True
        else:
            print(f"❌ Failed to get threats: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting threats: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("  DL-SEC System Test")
    print("=" * 60)
    
    tests = [
        ("Backend Connection", test_backend_connection),
        ("Dataset Load", test_dataset_load),
        ("Dataset Stats", test_dataset_stats),
        ("Threat Detection", test_threat_detection),
        ("Streaming Status", test_streaming_status),
        ("Threats Endpoint", test_threats_endpoint),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {str(e)}")
            results.append((test_name, False))
        time.sleep(1)  # Small delay between tests
    
    # Print summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print("=" * 60)
    print(f"  Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! The system is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

