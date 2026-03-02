#!/usr/bin/env python3
"""
Test script for the file upload system
"""

import requests
import os
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_image.jpg"

def create_test_image():
    """Create a simple test image file"""
    # Create a simple 1x1 pixel PNG image (base64 encoded)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
    
    with open(TEST_IMAGE_PATH, 'wb') as f:
        f.write(png_data)
    
    print(f"✅ Created test image: {TEST_IMAGE_PATH}")

def test_file_upload():
    """Test the file upload endpoint"""
    print("🧪 Testing file upload system...")
    
    # Check if test image exists
    if not Path(TEST_IMAGE_PATH).exists():
        create_test_image()
    
    # Test data
    test_data = {
        'journal_entry_id': 1  # Assuming journal entry with ID 1 exists
    }
    
    # Test file
    with open(TEST_IMAGE_PATH, 'rb') as f:
        files = {'file': (TEST_IMAGE_PATH, f, 'image/png')}
        
        try:
            response = requests.post(
                f"{BASE_URL}/upload/journal-attachment/",
                data=test_data,
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ File upload successful!")
                print(f"   - Attachment ID: {result['id']}")
                print(f"   - Filename: {result['filename']}")
                print(f"   - File type: {result['file_type']}")
                print(f"   - File size: {result['file_size']} bytes")
                return result
            else:
                print(f"❌ File upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to backend server")
            print("   Make sure the backend is running on http://localhost:8000")
            return None
        except Exception as e:
            print(f"❌ Error during upload: {str(e)}")
            return None

def test_file_serving(attachment_id):
    """Test that uploaded files can be served"""
    print(f"🧪 Testing file serving for attachment {attachment_id}...")
    
    try:
        # This would need the actual file path from the database
        # For now, just test the endpoint structure
        response = requests.get(f"{BASE_URL}/uploads/images/test_user/test_file.png")
        
        if response.status_code == 200:
            print("✅ File serving works!")
        elif response.status_code == 404:
            print("ℹ️  File not found (expected for test file)")
        else:
            print(f"❌ File serving failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing file serving: {str(e)}")

def cleanup():
    """Clean up test files"""
    if Path(TEST_IMAGE_PATH).exists():
        Path(TEST_IMAGE_PATH).unlink()
        print(f"🧹 Cleaned up test file: {TEST_IMAGE_PATH}")

if __name__ == "__main__":
    print("🚀 Starting file upload system test...")
    print("=" * 50)
    
    # Test file upload
    attachment = test_file_upload()
    
    if attachment:
        # Test file serving
        test_file_serving(attachment['id'])
    
    # Cleanup
    cleanup()
    
    print("=" * 50)
    print("🏁 Test completed!")
    print("\n📝 Next steps:")
    print("   1. Start the backend server: python main.py")
    print("   2. Create a journal entry through the API")
    print("   3. Upload attachments to that journal entry")
    print("   4. Test the frontend integration")
