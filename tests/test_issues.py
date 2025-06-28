import sys
import os
sys.path.append('/home/lelouch/Retail')

# Test script to reproduce the issues mentioned in the issue description

try:
    from RetailShop import app
    print("✓ Application imported successfully")
    
    with app.app_context():
        client = app.test_client()
        
        # Test 1: view_product route - should cause 'x' is undefined error
        print("\n=== Testing view_product route ===")
        try:
            response = client.get('/view_product/1')
            if response.status_code == 200:
                print("✓ /view_product/1 route accessible")
            elif response.status_code == 500:
                print("✗ /view_product/1 route caused server error (likely 'x' is undefined)")
            else:
                print(f"? /view_product/1 route returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing /view_product/1 route: {e}")
        
        # Test 2: cart route - should cause NoneType iteration error
        print("\n=== Testing cart route ===")
        try:
            # First, we need to simulate a logged-in user
            with client.session_transaction() as sess:
                sess['logged_in'] = True
                sess['uid'] = 1
                sess['s_name'] = 'Test User'
            
            response = client.get('/cart')
            if response.status_code == 200:
                print("✓ /cart route accessible")
            elif response.status_code == 500:
                print("✗ /cart route caused server error (likely NoneType iteration)")
            else:
                print(f"? /cart route returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing /cart route: {e}")
        
        # Test 3: Check if home page loads (to see BROWSE BY DRESS STYLE section)
        print("\n=== Testing home page (BROWSE BY DRESS STYLE) ===")
        try:
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Home page accessible")
                # Check if the response contains the BROWSE BY DRESS STYLE section
                if b'BROWSE BY DRESS STYLE' in response.data:
                    print("✓ BROWSE BY DRESS STYLE section found in home page")
                else:
                    print("✗ BROWSE BY DRESS STYLE section not found in home page")
            else:
                print(f"✗ Home page returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing home page: {e}")
            
    print("\nTest completed!")
    
except Exception as e:
    print(f"✗ Error importing application: {e}")
    import traceback
    traceback.print_exc()