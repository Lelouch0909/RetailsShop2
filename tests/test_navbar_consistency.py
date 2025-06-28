import sys
import os
sys.path.append('/home/lelouch/Retail')

# Test script to verify navbar consistency across pages

try:
    from RetailShop import app
    print("✓ Application imported successfully")

    with app.app_context():
        client = app.test_client()
        
        print("\n=== Testing Navbar Consistency Across Pages ===")
        
        # List of pages to test
        pages = [
            '/',                    # Home page
            '/all-products',        # Products page
            '/arrivals',            # Arrivals page
            '/sales',               # Sales page
            '/brands',              # Brands page
            '/login',               # Login page
            '/register'             # Register page
        ]
        
        # Check each page for the modern navbar
        for page in pages:
            try:
                response = client.get(page)
                if response.status_code == 200:
                    content = response.data.decode('utf-8')
                    
                    # Check for modern navbar elements
                    has_header_top = 'header-top' in content
                    has_nav_content = 'nav-content' in content
                    has_search_box = 'search-box' in content
                    has_modern_style = 'modern-style.css' in content
                    
                    if has_header_top and has_nav_content and has_search_box and has_modern_style:
                        print(f"✓ {page} has modern navbar")
                    else:
                        print(f"✗ {page} missing modern navbar elements:")
                        if not has_header_top:
                            print("  - Missing header-top")
                        if not has_nav_content:
                            print("  - Missing nav-content")
                        if not has_search_box:
                            print("  - Missing search-box")
                        if not has_modern_style:
                            print("  - Missing modern-style.css")
                else:
                    print(f"✗ {page} returned status code: {response.status_code}")
            except Exception as e:
                print(f"✗ Error accessing {page}: {e}")
        
        print("\nTest completed!")
    
except Exception as e:
    print(f"✗ Error importing application: {e}")
    import traceback
    traceback.print_exc()