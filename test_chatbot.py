#!/usr/bin/env python3
"""
Test script for Crittr Chatbot API
"""
import requests
import json
import time

def test_chatbot():
    """Test the integrated chatbot API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🤖 Testing Crittr Backend with Integrated Chatbot")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Homepage
    print("\n2. Testing homepage...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Homepage accessible")
            data = response.json()
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"❌ Homepage failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Homepage error: {e}")
    
    # Test 3: Query endpoint
    print("\n3. Testing query endpoint...")
    test_queries = [
        "What features does Crittr offer?",
        "How can I track my pet's health?",
        "Does Crittr have a mobile app?",
        "What is the AI assistant feature?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Test query {i}: {query}")
        try:
            payload = {"query": query}
            response = requests.post(
                f"{base_url}/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Query successful")
                print(f"   Model used: {data.get('model_used')}")
                print(f"   Response: {data.get('response')[:100]}...")
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Query error: {e}")
        
        # Small delay between queries
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    test_chatbot()
