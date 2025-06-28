import sys
import os
sys.path.append('/home/lelouch/Retail')

from RetailShop import app
from RetailShop.db_helper import execute_query
from passlib.hash import sha256_crypt
import random
import string

def generate_random_string(length=8):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def test_registration_and_login():
    """Test the registration and login flow"""
    client = app.test_client()

    # Generate random user data to avoid conflicts
    random_suffix = generate_random_string()
    test_name = f"Test User {random_suffix}"
    test_email = f"test{random_suffix}@example.com"
    test_username = f"testuser{random_suffix}"
    test_password = "password123"
    test_mobile = "12345678901"  # Must be at least 11 characters

    print(f"Testing registration with username: {test_username}")

    # Test registration
    response = client.post('/register', data={
        'name': test_name,
        'email': test_email,
        'username': test_username,
        'password': test_password,
        'mobile': test_mobile
    }, follow_redirects=True)

    # Check if registration was successful
    if b'You are now registered and can login' in response.data:
        print("✓ Registration successful")
    else:
        print("✗ Registration failed")
        print("Response data:")
        print(response.data.decode('utf-8'))
        return

    # Verify user was added to database
    with app.app_context():
        user = execute_query("SELECT * FROM users WHERE username=%s", [test_username], fetchone=True)

        if user:
            print("✓ User found in database")
            print(f"  - ID: {user['id']}")
            print(f"  - Name: {user['name']}")
            print(f"  - Email: {user['email']}")

            # Verify password was hashed
            if sha256_crypt.verify(test_password, user['password']):
                print("✓ Password was correctly hashed")
            else:
                print("✗ Password verification failed")
        else:
            print("✗ User not found in database")
            return

    # Test login
    response = client.post('/login', data={
        'username': test_username,
        'password': test_password
    }, follow_redirects=True)

    # Check if login was successful
    if b'You are logged out' not in response.data and b'Login' not in response.data:
        print("✓ Login successful")
    else:
        print("✗ Login failed")

    # Test navbar display after login
    if b'fa-sign-out-alt' in response.data and b'fa-sign-in-alt' not in response.data:
        print("✓ Navbar shows logout button when logged in")
    else:
        print("✗ Navbar does not show correct buttons when logged in")

    # Test logout
    response = client.get('/out', follow_redirects=True)

    # Check if logout was successful
    if b'You are logged out' in response.data:
        print("✓ Logout successful")
    else:
        print("✗ Logout failed")

    # Test navbar display after logout
    if b'fa-sign-in-alt' in response.data and b'fa-sign-out-alt' not in response.data:
        print("✓ Navbar shows login button when logged out")
    else:
        print("✗ Navbar does not show correct buttons when logged out")

    print("\nTest completed!")

if __name__ == "__main__":
    test_registration_and_login()
