import sys
import os
sys.path.append('/home/lelouch/Retail')

# Test if the application can be imported without errors
try:
    from RetailShop import app
    print("✓ Application imported successfully")
    
    # Test if min function is available in Jinja2 environment
    if 'min' in app.jinja_env.globals:
        print("✓ min function is available in Jinja2 environment")
    else:
        print("✗ min function is NOT available in Jinja2 environment")
    
    # Test if we can create an app context
    with app.app_context():
        print("✓ Application context created successfully")
        
        # Test if we can access the routes
        client = app.test_client()
        
        # Test the arrivals route (this was causing the error)
        try:
            response = client.get('/arrivals')
            if response.status_code in [200, 302]:  # 200 for success, 302 for redirect
                print("✓ /arrivals route accessible")
            else:
                print(f"✗ /arrivals route returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing /arrivals route: {e}")
        
        # Test the sales route
        try:
            response = client.get('/sales')
            if response.status_code in [200, 302]:
                print("✓ /sales route accessible")
            else:
                print(f"✗ /sales route returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing /sales route: {e}")
        
        # Test the brands route
        try:
            response = client.get('/brands')
            if response.status_code in [200, 302]:
                print("✓ /brands route accessible")
            else:
                print(f"✗ /brands route returned status code: {response.status_code}")
        except Exception as e:
            print(f"✗ Error accessing /brands route: {e}")
            
    print("\nTest completed!")
    
except Exception as e:
    print(f"✗ Error importing application: {e}")
    import traceback
    traceback.print_exc()