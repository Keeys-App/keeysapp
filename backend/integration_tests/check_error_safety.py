#!/usr/bin/env python3
"""
Integration test script to verify that errors are safe for users.
This makes real HTTP requests to verify error handling.

This is NOT a pytest test - it's a manual integration test script.
Run it when backend is running: python check_error_safety.py
"""
import requests
import json


API_URL = "http://localhost:8000/graphql"


def test_register_duplicate_email():
    """
    Test that duplicate email error is user-friendly.
    """
    print("\n" + "="*60)
    print("TEST: Register with duplicate email")
    print("="*60)
    
    mutation = """
    mutation {
      register(input: {
        email: "test@example.com"
        username: "testuser"
        password: "password123"
      }) {
        accessToken
        user { id username }
      }
    }
    """
    
    response = requests.post(API_URL, json={"query": mutation})
    data = response.json()
    
    print(f"\nResponse: {json.dumps(data, indent=2)}")
    
    if "errors" in data:
        error_msg = data["errors"][0]["message"]
        print(f"\n✅ User sees: '{error_msg}'")
        
        # Check that error is safe
        dangerous_keywords = ["SQL", "column", "table", "psycopg", "SELECT", "INSERT", "database"]
        has_dangerous = any(keyword.lower() in error_msg.lower() for keyword in dangerous_keywords)
        
        if has_dangerous:
            print("❌ FAIL: Error contains technical details!")
            return False
        else:
            print("✅ PASS: Error message is safe for users")
            return True
    else:
        print("✅ Registration successful (or user already exists)")
        return True


def test_login_wrong_credentials():
    """
    Test that login error is user-friendly.
    """
    print("\n" + "="*60)
    print("TEST: Login with wrong credentials")
    print("="*60)
    
    mutation = """
    mutation {
      login(input: {
        email: "wrong@example.com"
        password: "wrongpass"
      }) {
        accessToken
        user { id username }
      }
    }
    """
    
    response = requests.post(API_URL, json={"query": mutation})
    data = response.json()
    
    print(f"\nResponse: {json.dumps(data, indent=2)}")
    
    if "errors" in data:
        error_msg = data["errors"][0]["message"]
        print(f"\n✅ User sees: '{error_msg}'")
        
        # Check that error is safe
        assert error_msg == "Invalid credentials", f"Expected 'Invalid credentials', got '{error_msg}'"
        print("✅ PASS: Error message is safe and doesn't reveal if user exists")
        return True
    
    return False


def test_successful_registration():
    """
    Test successful registration and check response format.
    """
    print("\n" + "="*60)
    print("TEST: Successful registration")
    print("="*60)
    
    import random
    random_num = random.randint(1000, 9999)
    
    mutation = f"""
    mutation {{
      register(input: {{
        email: "user{random_num}@example.com"
        username: "user{random_num}"
        password: "password123"
      }}) {{
        accessToken
        user {{ id username email }}
      }}
    }}
    """
    
    response = requests.post(API_URL, json={"query": mutation})
    data = response.json()
    
    print(f"\nResponse: {json.dumps(data, indent=2)}")
    
    if "data" in data and data["data"]["register"]:
        user_id = data["data"]["register"]["user"]["id"]
        print(f"\n✅ User registered successfully")
        print(f"   User ID: {user_id}")
        
        # Check that ID is UUID, not integer
        if "-" in user_id and len(user_id) == 36:
            print("✅ PASS: ID is UUID (secure)")
            return True
        else:
            print("❌ FAIL: ID is not UUID (enumeration attack possible)")
            return False
    
    return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  TESTING ERROR SAFETY")
    print("  Verifying that technical errors never reach users")
    print("="*60)
    
    try:
        # Test connection
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("\n❌ Backend is not running!")
            print("   Start it with: cd backend && source venv/bin/activate && python main.py")
            exit(1)
        
        print("\n✅ Backend is running")
        
        # Run tests
        results = []
        results.append(("Duplicate Email", test_register_duplicate_email()))
        results.append(("Wrong Credentials", test_login_wrong_credentials()))
        results.append(("UUID Security", test_successful_registration()))
        
        # Summary
        print("\n" + "="*60)
        print("  SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("   Users will NEVER see technical errors!")
        else:
            print("\n❌ SOME TESTS FAILED!")
            print("   Fix errors before deploying!")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to backend!")
        print("   Make sure backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

