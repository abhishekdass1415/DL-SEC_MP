#load_test_dataset.py
#!/usr/bin/env python3
"""
Script to load and process the test dataset for DL-SEC threat detection system.
This script loads the UNSW_NB15 testing dataset and processes it through the model.
"""

import os
import sys
import requests
import time
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = "http://localhost:5000/api"

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/model/status")
        if response.status_code == 200:
            print("✓ Server is running")
            return True
        else:
            print("✗ Server is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running. Please start the backend server first.")
        return False

def load_test_dataset(file_path):
    """Load the test dataset"""
    print(f"\n📁 Loading dataset: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"✗ Dataset file not found: {file_path}")
        return False
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dataset/load",
            json={"file_path": file_path}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Dataset loaded successfully")
            print(f"  - Total records: {data.get('total_records', 0)}")
            print(f"  - Columns: {len(data.get('columns', []))}")
            return True
        else:
            print(f"✗ Error loading dataset: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def get_dataset_stats():
    """Get dataset statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/dataset/stats")
        if response.status_code == 200:
            stats = response.json()
            print("\n📊 Dataset Statistics:")
            print(f"  - Total records: {stats.get('total_records', 0)}")
            print(f"  - Current index: {stats.get('current_index', 0)}")
            print(f"  - Remaining records: {stats.get('remaining_records', 0)}")
            if 'threats' in stats:
                print(f"  - Threats: {stats.get('threats', 0)}")
                print(f"  - Normal: {stats.get('normal', 0)}")
                print(f"  - Threat percentage: {stats.get('threat_percentage', 0)}%")
            return stats
        else:
            print(f"✗ Error getting stats: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None

def process_single_record():
    """Process a single record from the dataset"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/dataset/process",
            json={"batch_size": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            prediction = data.get('prediction', {})
            
            if data.get('threat_detected'):
                threat = data.get('threat', {})
                print(f"  ⚠️  Threat detected: {threat.get('threat_type')} (Confidence: {prediction.get('confidence', 0):.2%})")
                return True
            else:
                print(f"  ✓ Normal activity (Confidence: {prediction.get('confidence', 0):.2%})")
                return False
        else:
            print(f"  ✗ Error processing record: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def start_streaming(interval=2.0, max_records=None):
    """Start streaming dataset in real-time"""
    print(f"\n🔄 Starting real-time streaming (interval: {interval}s)")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dataset/stream/start",
            json={"interval": interval, "use_dataset": True}
        )
        
        if response.status_code == 200:
            print("✓ Streaming started")
            print("  Press Ctrl+C to stop streaming")
            
            # Monitor streaming
            records_processed = 0
            threats_detected = 0
            
            try:
                while True:
                    time.sleep(interval)
                    
                    # Check streaming status
                    status_response = requests.get(f"{API_BASE_URL}/dataset/stream/status")
                    if status_response.status_code == 200:
                        status = status_response.json()
                        if not status.get('is_running'):
                            print("\n✓ Streaming completed")
                            break
                    
                    # Get stats periodically
                    stats = get_dataset_stats()
                    if stats:
                        records_processed = stats.get('current_index', 0)
                        if records_processed % 10 == 0:
                            print(f"  Processed {records_processed} records...")
                    
            except KeyboardInterrupt:
                print("\n🛑 Stopping streaming...")
                stop_response = requests.post(f"{API_BASE_URL}/dataset/stream/stop")
                if stop_response.status_code == 200:
                    print("✓ Streaming stopped")
            
            return True
        else:
            print(f"✗ Error starting streaming: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def process_batch(batch_size=10):
    """Process a batch of records"""
    print(f"\n📦 Processing batch of {batch_size} records...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/dataset/process",
            json={"batch_size": batch_size}
        )
        
        if response.status_code == 200:
            data = response.json()
            processed = data.get('processed', 0)
            results = data.get('results', [])
            
            threats = sum(1 for r in results if r.get('prediction', {}).get('is_threat'))
            
            print(f"✓ Processed {processed} records")
            print(f"  - Threats detected: {threats}")
            print(f"  - Normal activity: {processed - threats}")
            
            return True
        else:
            print(f"✗ Error processing batch: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("  DL-SEC Test Dataset Loader")
    print("=" * 60)
    
    # Check if server is running
    if not check_server():
        return
    
    # Get dataset path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_dataset_path = os.path.join(project_root, "UNSW_NB15_testing-set.csv")
    
    if not os.path.exists(test_dataset_path):
        print(f"\n✗ Test dataset not found at: {test_dataset_path}")
        print("  Please ensure UNSW_NB15_testing-set.csv is in the project root directory.")
        return
    
    # Load dataset
    if not load_test_dataset(test_dataset_path):
        return
    
    # Get dataset stats
    get_dataset_stats()
    
    # Ask user what to do
    print("\n" + "=" * 60)
    print("What would you like to do?")
    print("1. Process single record")
    print("2. Process batch of records")
    print("3. Start real-time streaming")
    print("4. Exit")
    print("=" * 60)
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        process_single_record()
    elif choice == "2":
        batch_size = input("Enter batch size (default: 10): ").strip()
        batch_size = int(batch_size) if batch_size else 10
        process_batch(batch_size)
    elif choice == "3":
        interval = input("Enter streaming interval in seconds (default: 2.0): ").strip()
        interval = float(interval) if interval else 2.0
        start_streaming(interval)
    elif choice == "4":
        print("Exiting...")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()

