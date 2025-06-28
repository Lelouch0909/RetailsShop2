import sys
import os
sys.path.append('/home/lelouch/Retail')

try:
    from RetailShop import app
    print("✓ Application imported successfully")

    with app.app_context():
        from RetailShop.db_helper import execute_query
        
        # Check admin table structure
        print("\n=== Admin Table Structure ===")
        try:
            structure = execute_query("DESCRIBE admin", (), fetchall=True)
            for field in structure:
                print(f"Field: {field['Field']}, Type: {field['Type']}, Null: {field['Null']}, Default: {field['Default']}")
        except Exception as e:
            print(f"Error getting table structure: {e}")
        
        # Create a proper admin user
        print("\n=== Creating Proper Admin User ===")
        import hashlib
        
        test_email = "admin@shoptub.com"
        test_password = "admin123"
        hashed_password = hashlib.sha256(test_password.encode()).hexdigest()
        
        try:
            # Check if admin already exists
            existing = execute_query("SELECT * FROM admin WHERE email=%s", (test_email,), fetchone=True)
            
            if existing:
                print(f"✓ Admin user already exists: {test_email}")
                print(f"Email: {test_email}")
                print(f"Password: {test_password}")
            else:
                # Insert with all required fields
                execute_query(
                    "INSERT INTO admin (email, password, firstName, lastName, mobile) VALUES (%s, %s, %s, %s, %s)",
                    (test_email, hashed_password, "Admin", "User", "1234567890"),
                    commit=True
                )
                print(f"✓ Created admin user: {test_email}")
                print(f"Email: {test_email}")
                print(f"Password: {test_password}")
                
        except Exception as e:
            print(f"✗ Error with admin user: {e}")
        
        # Test dropdown functionality more thoroughly
        print("\n=== Testing Dropdown Issues ===")
        client = app.test_client()
        
        # Test home page
        response = client.get('/')
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            
            # Check for potential conflicts
            print("Checking for potential JavaScript conflicts:")
            
            # Check if both Bootstrap and custom scripts are loaded
            if 'bootstrap.min.js' in content:
                print("✓ Bootstrap JS is loaded")
            else:
                print("✗ Bootstrap JS not found")
                
            if 'modern-script.js' in content:
                print("✓ Modern script is loaded")
            else:
                print("✗ Modern script not found")
                
            # Check dropdown structure
            if 'data-toggle="dropdown"' in content:
                print("✓ Bootstrap 4 dropdown syntax found")
            elif 'data-bs-toggle="dropdown"' in content:
                print("! Bootstrap 5 dropdown syntax found (might cause conflicts)")
            else:
                print("✗ No dropdown toggle found")
                
            # Check for jQuery
            if 'jquery' in content.lower():
                print("✓ jQuery is loaded")
            else:
                print("✗ jQuery not found")
        
        # Test view all button functionality
        print("\n=== Testing View All Button Routes ===")
        
        routes_to_test = ['/arrivals', '/sales', '/all-products']
        for route in routes_to_test:
            try:
                response = client.get(route)
                if response.status_code == 200:
                    print(f"✓ {route} is accessible")
                else:
                    print(f"✗ {route} returned status {response.status_code}")
            except Exception as e:
                print(f"✗ Error accessing {route}: {e}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()