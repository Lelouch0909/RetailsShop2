from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from RetailShop.db_helper import execute_query
import datetime

# Create a Blueprint for likes and reviews
likes_reviews = Blueprint('likes_reviews', __name__)

# Initialize database tables if they don't exist
@likes_reviews.before_app_first_request
def initialize_tables():
    # Create likes table
    execute_query("""
        CREATE TABLE IF NOT EXISTS product_likes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_product (user_id, product_id)
        )
    """, commit=True)
    
    # Create reviews table
    execute_query("""
        CREATE TABLE IF NOT EXISTS product_reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            rating INT NOT NULL,
            review_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_product_review (user_id, product_id)
        )
    """, commit=True)

# Route to like/unlike a product
@likes_reviews.route('/like_product/<int:product_id>', methods=['POST'])
def like_product(product_id):
    if 'uid' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Please login to like products'}), 401
        flash('Please login to like products', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['uid']
    
    # Check if user already liked the product
    existing_like = execute_query(
        "SELECT * FROM product_likes WHERE user_id = %s AND product_id = %s",
        (user_id, product_id),
        fetchone=True
    )
    
    if existing_like:
        # Unlike the product
        execute_query(
            "DELETE FROM product_likes WHERE user_id = %s AND product_id = %s",
            (user_id, product_id),
            commit=True
        )
        action = 'unliked'
    else:
        # Like the product
        execute_query(
            "INSERT INTO product_likes (user_id, product_id) VALUES (%s, %s)",
            (user_id, product_id),
            commit=True
        )
        action = 'liked'
    
    # Get total likes for the product
    likes_count = execute_query(
        "SELECT COUNT(*) as count FROM product_likes WHERE product_id = %s",
        (product_id,),
        fetchone=True
    )
    
    count = likes_count['count'] if likes_count else 0
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'action': action,
            'likes_count': count
        })
    
    # If not AJAX request, redirect back to product page
    return redirect(url_for('view_product', product_id=product_id))

# Route to get likes count for a product
@likes_reviews.route('/get_likes/<int:product_id>', methods=['GET'])
def get_likes(product_id):
    # Get total likes for the product
    likes_count = execute_query(
        "SELECT COUNT(*) as count FROM product_likes WHERE product_id = %s",
        (product_id,),
        fetchone=True
    )
    
    count = likes_count['count'] if likes_count else 0
    
    # Check if current user has liked the product
    user_liked = False
    if 'uid' in session:
        user_id = session['uid']
        user_like = execute_query(
            "SELECT * FROM product_likes WHERE user_id = %s AND product_id = %s",
            (user_id, product_id),
            fetchone=True
        )
        user_liked = user_like is not None
    
    return jsonify({
        'likes_count': count,
        'user_liked': user_liked
    })

# Route to add a review for a product
@likes_reviews.route('/add_review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    if 'uid' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Please login to review products'}), 401
        flash('Please login to review products', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['uid']
    rating = request.form.get('rating')
    review_text = request.form.get('review_text')
    
    if not rating or not review_text:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Rating and review text are required'}), 400
        flash('Rating and review text are required', 'danger')
        return redirect(url_for('view_product', product_id=product_id))
    
    # Check if user already reviewed the product
    existing_review = execute_query(
        "SELECT * FROM product_reviews WHERE user_id = %s AND product_id = %s",
        (user_id, product_id),
        fetchone=True
    )
    
    if existing_review:
        # Update existing review
        execute_query(
            "UPDATE product_reviews SET rating = %s, review_text = %s, created_at = NOW() WHERE user_id = %s AND product_id = %s",
            (rating, review_text, user_id, product_id),
            commit=True
        )
        message = 'Review updated successfully'
    else:
        # Add new review
        execute_query(
            "INSERT INTO product_reviews (user_id, product_id, rating, review_text) VALUES (%s, %s, %s, %s)",
            (user_id, product_id, rating, review_text),
            commit=True
        )
        message = 'Review added successfully'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Get user info for the review
        user_info = execute_query(
            "SELECT name FROM users WHERE id = %s",
            (user_id,),
            fetchone=True
        )
        
        user_name = user_info['name'] if user_info else 'Anonymous'
        
        return jsonify({
            'status': 'success',
            'message': message,
            'review': {
                'user_name': user_name,
                'rating': int(rating),
                'review_text': review_text,
                'created_at': datetime.datetime.now().strftime("%B %d, %Y")
            }
        })
    
    flash(message, 'success')
    return redirect(url_for('view_product', product_id=product_id))

# Route to get reviews for a product
@likes_reviews.route('/get_reviews/<int:product_id>', methods=['GET'])
def get_reviews(product_id):
    # Get all reviews for the product
    reviews = execute_query(
        """
        SELECT r.*, u.name as user_name
        FROM product_reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.product_id = %s
        ORDER BY r.created_at DESC
        """,
        (product_id,),
        fetchall=True
    )
    
    # Get average rating
    avg_rating = execute_query(
        "SELECT AVG(rating) as avg_rating FROM product_reviews WHERE product_id = %s",
        (product_id,),
        fetchone=True
    )
    
    average = avg_rating['avg_rating'] if avg_rating and avg_rating['avg_rating'] else 0
    
    # Get rating distribution
    rating_distribution = execute_query(
        """
        SELECT rating, COUNT(*) as count
        FROM product_reviews
        WHERE product_id = %s
        GROUP BY rating
        ORDER BY rating DESC
        """,
        (product_id,),
        fetchall=True
    )
    
    # Format the reviews for JSON response
    formatted_reviews = []
    if reviews:
        for review in reviews:
            formatted_reviews.append({
                'id': review['id'],
                'user_name': review['user_name'],
                'rating': review['rating'],
                'review_text': review['review_text'],
                'created_at': review['created_at'].strftime("%B %d, %Y")
            })
    
    # Format rating distribution
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    if rating_distribution:
        for rating in rating_distribution:
            distribution[rating['rating']] = rating['count']
    
    return jsonify({
        'reviews': formatted_reviews,
        'average_rating': round(float(average), 1) if average else 0,
        'total_reviews': len(formatted_reviews),
        'rating_distribution': distribution
    })