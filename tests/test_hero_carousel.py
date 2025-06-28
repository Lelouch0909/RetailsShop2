import sys
import os
sys.path.append('/home/lelouch/Retail')

try:
    from RetailShop import app
    print("✓ Application imported successfully")

    with app.app_context():
        client = app.test_client()
        
        print("\n=== Testing Hero Carousel Implementation ===")
        
        # Test if home page loads
        response = client.get('/')
        if response.status_code == 200:
            print("✓ Home page accessible")
            content = response.data.decode('utf-8')
            
            # Check if carousel exists
            if 'id="heroCarousel"' in content:
                print("✓ Hero carousel found in home page")
                
                # Check if carousel has data attributes for auto-cycling
                if 'data-interval="3000"' in content:
                    print("✓ Carousel has auto-cycling enabled")
                else:
                    print("✗ Carousel missing auto-cycling configuration")
                
                # Check if carousel indicators exist
                if 'carousel-indicators' in content:
                    print("✓ Carousel indicators found")
                else:
                    print("✗ Carousel indicators missing")
                
                # Check if carousel has product images
                if 'carousel-item' in content and 'image/product/' in content:
                    print("✓ Carousel contains product images")
                else:
                    print("✗ Carousel does not contain product images")
                
                # Check if carousel has navigation controls
                if 'carousel-control-prev' in content and 'carousel-control-next' in content:
                    print("✓ Carousel navigation controls found")
                else:
                    print("✗ Carousel navigation controls missing")
                
                # Check if stars are still present
                if 'star star-1' in content and 'star star-2' in content:
                    print("✓ Star elements preserved")
                else:
                    print("✗ Star elements missing")
                
            else:
                print("✗ Hero carousel not found in home page")
        else:
            print(f"✗ Home page returned status code: {response.status_code}")
            
        print("\nTest completed!")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()