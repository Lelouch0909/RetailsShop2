import sys
import os
sys.path.append('/home/lelouch/Retail')

# Test script to reproduce the UI issues mentioned in the issue description

try:
    from RetailShop import app
    print("✓ Application imported successfully")

    with app.app_context():
        client = app.test_client()

        # Test 1: Check if /all-products shows "Unauthorised" errors
        print("\n=== Testing /all-products route ===")
        try:
            response = client.get('/all-products')
            if response.status_code == 200:
                print("✓ /all-products route accessible")
                # Check if response contains "Unauthorised"
                if b'Unauthorised' in response.data:
                    print("✗ /all-products contains 'Unauthorised' text")
                    # Count occurrences
                    count = response.data.count(b'Unauthorised')
                    print(f"   Found {count} occurrences of 'Unauthorised'")
                else:
                    print("✓ /all-products does not contain 'Unauthorised' text")
            else:
                print(f"✗ /all-products route returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing /all-products route: {e}")

        # Test 2: Check home page for navbar and login button issues
        print("\n=== Testing home page (navbar and login button) ===")
        try:
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Home page accessible")

                # Check if navbar contains dropdown
                if b'dropdown-toggle' in response.data:
                    print("✓ Navbar dropdown elements found")
                else:
                    print("✗ Navbar dropdown elements not found")

                # Check login button when not logged in
                if 'Connexion'.encode('utf-8') in response.data:
                    print("✓ Login button found when not logged in")
                else:
                    print("✗ Login button not found when not logged in")

            else:
                print(f"✗ Home page returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing home page: {e}")

        # Test 3: Check logged in state
        print("\n=== Testing logged in state ===")
        try:
            # Simulate logged in user
            with client.session_transaction() as sess:
                sess['logged_in'] = True
                sess['uid'] = 1
                sess['s_name'] = 'Test User'

            response = client.get('/')
            if response.status_code == 200:
                print("✓ Home page accessible when logged in")

                # Check if logout button appears
                if 'Déconnexion'.encode('utf-8') in response.data:
                    print("✓ Logout button found when logged in")
                else:
                    print("✗ Logout button not found when logged in")

                # Check if login button is hidden
                if 'Connexion'.encode('utf-8') in response.data:
                    print("✗ Login button still visible when logged in")
                else:
                    print("✓ Login button hidden when logged in")

            else:
                print(f"✗ Home page returned status code when logged in: {response.status_code}")
        except Exception as e:
            print(f"✗ Error testing logged in state: {e}")

    print("\nTest completed!")

except Exception as e:
    print(f"✗ Error importing application: {e}")
    import traceback
    traceback.print_exc()
