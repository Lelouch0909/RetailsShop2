import sys
import os
sys.path.append('/home/lelouch/Retail')

# Test script to check current issues

try:
    from RetailShop import app
    print("✓ Application imported successfully")

    with app.app_context():
        client = app.test_client()

        # Test 1: Check home page dropdown functionality
        print("\n=== Testing home page dropdown ===")
        try:
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Home page accessible")
                
                # Check dropdown structure
                content = response.data.decode('utf-8')
                if 'dropdown-toggle' in content and 'dropdown-menu' in content:
                    print("✓ Dropdown structure present")
                    
                    # Check if JavaScript is properly loaded
                    if 'modern-script.js' in content:
                        print("✓ Modern script loaded")
                    else:
                        print("✗ Modern script not loaded")
                else:
                    print("✗ Dropdown structure missing")
                    
            else:
                print(f"✗ Home page returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing home page: {e}")

        # Test 2: Check view all buttons functionality
        print("\n=== Testing view all buttons ===")
        try:
            response = client.get('/')
            if response.status_code == 200:
                content = response.data.decode('utf-8')
                
                # Check if view all buttons exist
                if 'view-all-btn' in content:
                    print("✓ View all buttons found in HTML")
                    
                    # Check if JavaScript handles them
                    js_response = client.get('/static/js/modern-script.js')
                    if js_response.status_code == 200:
                        js_content = js_response.data.decode('utf-8')
                        if 'view-all-btn' in js_content:
                            print("✓ View all button handlers found in JavaScript")
                        else:
                            print("✗ View all button handlers missing in JavaScript")
                    else:
                        print("✗ JavaScript file not accessible")
                else:
                    print("✗ View all buttons not found in HTML")
        except Exception as e:
            print(f"✗ Error testing view all buttons: {e}")

        # Test 3: Check admin credentials
        print("\n=== Testing admin credentials ===")
        try:
            from RetailShop.db_helper import execute_query
            
            # Check if admin table exists and get admin users
            admins = execute_query("SELECT * FROM admin", (), fetchall=True)
            
            if admins:
                print(f"✓ Found {len(admins)} admin user(s)")
                for admin in admins:
                    print(f"   Admin ID: {admin['id']}, Email: {admin['email']}, Name: {admin.get('firstName', 'N/A')}")
            else:
                print("✗ No admin users found")
                
                # Check if admin table exists
                try:
                    execute_query("DESCRIBE admin", (), fetchall=True)
                    print("✓ Admin table exists but is empty")
                except Exception as e:
                    print(f"✗ Admin table might not exist: {e}")
                    
        except Exception as e:
            print(f"✗ Error checking admin credentials: {e}")

    print("\nTest completed!")

except Exception as e:
    print(f"✗ Error importing application: {e}")
    import traceback
    traceback.print_exc()