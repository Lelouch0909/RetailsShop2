import sys
import os
sys.path.append('/home/lelouch/Retail')

from RetailShop import app

# Test the authentication flow and error pages
def test_auth_and_errors():
    client = app.test_client()

    print("Testing authentication flow and error pages...")

    # Test 404 error page
    try:
        response = client.get('/nonexistent_page')
        if response.status_code == 404 and b'404' in response.data and b'Oops! La page que vous recherchez n\'existe pas.' in response.data:
            print("✓ 404 error page works correctly")
        else:
            print(f"✗ 404 error page not working as expected. Status code: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing 404 page: {e}")

    # Test login and add to cart flow
    try:
        # First, try to access add_to_cart without being logged in
        response = client.post('/add_to_cart', data={
            'product_id': '1',
            'quantity': '1'
        }, follow_redirects=False)

        # Should be redirected to login page
        if response.status_code == 302 and '/login' in response.location:
            print("✓ Redirected to login page when trying to add to cart without being logged in")
        else:
            print(f"✗ Not redirected to login page when trying to add to cart without being logged in. Status: {response.status_code}, Location: {response.location if hasattr(response, 'location') else 'None'}")

        # Now login
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['uid'] = 1
            sess['s_name'] = 'Test User'

        # Try to add to cart again
        response = client.post('/add_to_cart', data={
            'product_id': '1',
            'quantity': '1'
        }, follow_redirects=True)

        # Should not be redirected to login page
        if b'Login' not in response.data:
            print("✓ Not redirected to login page when trying to add to cart while logged in")
        else:
            print("✗ Redirected to login page when trying to add to cart while logged in")

    except Exception as e:
        print(f"✗ Error testing authentication flow: {e}")

    print("\nTest completed!")

if __name__ == "__main__":
    test_auth_and_errors()
