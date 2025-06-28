import sys
import os
sys.path.append('/home/lelouch/Retail')

# Test script to verify dropdown functionality

try:
    from RetailShop import app
    print("✓ Application imported successfully")

    with app.app_context():
        client = app.test_client()

        # Test 1: Check if home page loads and contains proper dropdown structure
        print("\n=== Testing home page dropdown structure ===")
        try:
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Home page accessible")
                
                # Check for dropdown toggle with correct Bootstrap 4 syntax
                if b'data-toggle="dropdown"' in response.data:
                    print("✓ Dropdown uses correct Bootstrap 4 syntax (data-toggle)")
                else:
                    print("✗ Dropdown does not use correct Bootstrap 4 syntax")
                
                # Check for dropdown-item class
                if b'dropdown-item' in response.data:
                    print("✓ Dropdown items use correct Bootstrap 4 class (dropdown-item)")
                else:
                    print("✗ Dropdown items do not use correct Bootstrap 4 class")
                
                # Check for dropdown menu structure
                if b'class="dropdown-menu"' in response.data:
                    print("✓ Dropdown menu has correct structure")
                else:
                    print("✗ Dropdown menu structure is incorrect")
                
                # Check if modern-script.js is loaded
                if b'modern-script.js' in response.data:
                    print("✓ Modern script is loaded")
                else:
                    print("✗ Modern script is not loaded")
                    
            else:
                print(f"✗ Home page returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing home page: {e}")

        # Test 2: Check other pages for comparison
        print("\n=== Testing other pages dropdown structure ===")
        try:
            # Test a page that uses the layout.html template
            response = client.get('/all-products')
            if response.status_code == 200:
                print("✓ /all-products page accessible")
                
                # Check for dropdown structure in other pages
                if b'data-toggle="dropdown"' in response.data:
                    print("✓ Other pages also use Bootstrap 4 syntax")
                else:
                    print("? Other pages might use different syntax")
                    
            else:
                print(f"? /all-products page returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing /all-products page: {e}")

        # Test 3: Check if CSS and JS files exist
        print("\n=== Testing static files ===")
        try:
            css_response = client.get('/static/css/modern-style.css')
            if css_response.status_code == 200:
                print("✓ Modern CSS file accessible")
                
                # Check if dropdown styles are present
                if b'dropdown-menu' in css_response.data:
                    print("✓ Dropdown styles are present in CSS")
                else:
                    print("✗ Dropdown styles are missing in CSS")
            else:
                print(f"✗ Modern CSS file returned status code: {css_response.status_code}")
                
            js_response = client.get('/static/js/modern-script.js')
            if js_response.status_code == 200:
                print("✓ Modern JS file accessible")
                
                # Check if dropdown functionality is present
                if b'dropdown-toggle' in js_response.data:
                    print("✓ Dropdown functionality is present in JS")
                else:
                    print("✗ Dropdown functionality is missing in JS")
            else:
                print(f"✗ Modern JS file returned status code: {js_response.status_code}")
                
        except Exception as e:
            print(f"✗ Error accessing static files: {e}")

    print("\nTest completed!")
    print("\nNote: This test checks the structure and file accessibility.")
    print("To fully test dropdown functionality, you need to:")
    print("1. Start the Flask application: python app.py")
    print("2. Open http://127.0.0.1:5000/ in a browser")
    print("3. Click on the 'Shop' dropdown to test functionality")
    print("4. Verify that the dropdown opens and stays open when hovering")
    print("5. Verify that clicking on dropdown items navigates correctly")

except Exception as e:
    print(f"✗ Error importing application: {e}")
    import traceback
    traceback.print_exc()