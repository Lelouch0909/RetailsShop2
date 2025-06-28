import sys
import os
sys.path.append('/home/lelouch/Retail')

from RetailShop import app
from RetailShop.db_helper import execute_query

def test_auth_session():
    """Test the authentication session and navbar display"""
    client = app.test_client()

    print("Testing authentication session and navbar display...")

    # Test navbar display when not logged in
    response = client.get('/')

    response_text = response.data.decode('utf-8')
    if 'Inscription' in response_text and 'Connexion' in response_text and 'Déconnexion' not in response_text:
        print("✓ Navbar shows login/register buttons when not logged in")
    else:
        print("✗ Navbar does not show correct buttons when not logged in")

    # Simulate a logged-in user by setting session variables
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['uid'] = 1
        sess['s_name'] = 'Test User'

    # Test navbar display when logged in
    response = client.get('/')

    response_text = response.data.decode('utf-8')
    if 'Déconnexion' in response_text and 'Profil' in response_text and 'Panier' in response_text and 'Inscription' not in response_text and 'Connexion' not in response_text:
        print("✓ Navbar shows logout/profile/cart buttons when logged in")
    else:
        print("✗ Navbar does not show correct buttons when logged in")

    # Test accessing a protected route when logged in
    response = client.get('/cart')

    if response.status_code == 200:
        print("✓ Can access protected route when logged in")
    else:
        print(f"✗ Cannot access protected route when logged in. Status code: {response.status_code}")

    # Test logout
    response = client.get('/out', follow_redirects=True)

    # Check if session is cleared after logout
    with client.session_transaction() as sess:
        if 'logged_in' not in sess and 'uid' not in sess and 's_name' not in sess:
            print("✓ Logout successful (session cleared)")
        else:
            print("✗ Logout failed (session not cleared)")

    # Also check response text for logout message
    response_text = response.data.decode('utf-8')
    if 'You are logged out' in response_text:
        print("✓ Logout message displayed")
    else:
        print("✗ Logout message not displayed")

    # Test navbar display after logout
    if 'Inscription' in response_text and 'Connexion' in response_text and 'Déconnexion' not in response_text:
        print("✓ Navbar shows login/register buttons after logout")
    else:
        print("✗ Navbar does not show correct buttons after logout")

    # Test accessing a protected route when not logged in
    response = client.get('/cart')

    if response.status_code == 302 and '/login' in response.headers.get('Location', ''):
        print("✓ Redirected to login page when accessing protected route while not logged in")
    else:
        print(f"✗ Not redirected to login page when accessing protected route while not logged in. Status code: {response.status_code}")

    print("\nTest completed!")

if __name__ == "__main__":
    test_auth_session()
