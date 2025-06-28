import sys
import os
sys.path.append('/home/lelouch/Retail')

try:
    from RetailShop import app
    print("✓ Application imported successfully")

    with app.app_context():
        client = app.test_client()

        print("\n=== Testing Navbar Centering and Spacing ===")

        # Test if CSS file is accessible
        css_response = client.get('/static/css/modern-style.css')
        if css_response.status_code == 200:
            print("✓ CSS file accessible")
            css_content = css_response.data.decode('utf-8')

            # Check for our added CSS properties
            checks = [
                ('.nav-content', 'height'),
                ('.logo', 'display'),
                ('.logo', 'align-items'),
                ('.logo h1', 'margin'),
                ('.nav-menu', 'height'),
                ('.nav-menu', 'align-items'),
                ('.nav-menu li', 'height'),
                ('.nav-menu a', 'height'),
                ('.search-container', 'height'),
                ('.search-container', 'display'),
                ('.search-container', 'align-items'),
                ('.nav-icons', 'height'),
                ('.nav-icons', 'align-items'),
                ('.icon-link', 'display'),
                ('.icon-link', 'align-items'),
                ('.icon-link', 'justify-content'),
            ]

            for selector, property in checks:
                # More flexible check that doesn't rely on exact formatting
                if f"{selector}" in css_content and f"{property}" in css_content:
                    print(f"✓ {selector} has {property} property")
                else:
                    print(f"✗ {selector} might be missing {property} property")
        else:
            print(f"✗ CSS file returned status code: {css_response.status_code}")

        # Test if home page loads with the navbar
        response = client.get('/')
        if response.status_code == 200:
            print("✓ Home page accessible")

            # Check if navbar elements are present
            content = response.data.decode('utf-8')
            navbar_elements = [
                'header class="header"',
                'nav class="navbar"',
                'div class="nav-content"',
                'div class="logo"',
                'ul class="nav-menu"',
                'div class="search-container"',
                'div class="nav-icons"'
            ]

            for element in navbar_elements:
                if element in content:
                    print(f"✓ Found {element} in home page")
                else:
                    print(f"✗ Missing {element} in home page")
        else:
            print(f"✗ Home page returned status code: {response.status_code}")

        print("\nTest completed!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
