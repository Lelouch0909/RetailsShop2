import sys
import os
sys.path.append('/home/lelouch/Retail')

from flask import session, get_flashed_messages
from RetailShop import app

def test_flash_messages():
    """Test if flash messages are set and displayed correctly"""
    with app.test_client() as client:
        # Enable session in the test client
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['uid'] = 1
            sess['s_name'] = 'Test User'
        
        # Test logout
        response = client.get('/out', follow_redirects=True)
        
        # Get the HTML response
        html = response.data.decode('utf-8')
        
        # Check if the flash message is in the HTML
        if 'You are logged out' in html:
            print("✓ Flash message found in HTML response")
        else:
            print("✗ Flash message not found in HTML response")
            
        # Print part of the HTML to see what's there
        print("\nHTML snippet:")
        print(html[:500] + "...")
        
        # Check if we're redirected to the index page
        if 'SHOP.CO' in html:
            print("✓ Redirected to index page")
        else:
            print("✗ Not redirected to index page")

if __name__ == "__main__":
    test_flash_messages()