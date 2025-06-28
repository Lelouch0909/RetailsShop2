from flask import Flask, redirect, url_for, session, render_template
from flask_pymysql import MySQL
from functools import wraps
from flask_uploads import UploadSet, configure_uploads, IMAGES
import os


app = Flask(__name__)

# Add min function to Jinja2 environment
app.jinja_env.globals.update(min=min)

app.secret_key = os.urandom(24)

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'image', 'product')

upload_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'image', 'product')

os.makedirs(upload_path, exist_ok=True)

photos = UploadSet('photos', IMAGES)

configure_uploads(app, photos)

mysql = MySQL()

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'h'
app.config['MYSQL_DB'] = 'menshut'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql.init_app(app)

# Test connection
try:
    with app.app_context():
        conn = mysql.connection
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()['DATABASE()']
            print(f"Successfully connected to database: {db_name}")
            cursor.close()
        else:
            print("MySQL connection failed: connection object is None")
            print("This could be due to:")
            print("1. MySQL server is not running")
            print("2. Database 'shoptub' does not exist")
            print("3. User 'webapp' does not have access to the database")
            print("4. Password is incorrect")
except Exception as e:
    print(f"Error connecting to MySQL: {e}")
    print("Please check if MySQL server is running and the credentials are correct.")
    print("Database: shoptub, User: webapp, Password: motdepassefort")


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


def not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, *kwargs)

    return wrap


def is_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('admin_login'))

    return wrap


def not_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return redirect(url_for('admin'))
        else:
            return f(*args, *kwargs)

    return wrap


def wrappers(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped


def content_based_filtering(product_id):
    try:
        from RetailShop.db_helper import get_db, execute_query

        # Get product details
        product = execute_query("SELECT * FROM products WHERE id=%s", (product_id,), fetchone=True)
        if not product:
            print(f"No product found with ID: {product_id}")
            return ''

        data_cat = product['category']  # get id category ex shirt
        print('Showing result for Product Id: ' + str(product_id))

        # Get all products in the same category
        cat_products = execute_query("SELECT * FROM products WHERE category=%s", (data_cat,), fetchall=True)
        if not cat_products:
            print(f"No products found in category: {data_cat}")
            return ''

        category_matched = len(cat_products)
        print('Total product matched: ' + str(category_matched))

        # Get product level info
        id_level = execute_query("SELECT * FROM product_level WHERE product_id=%s", (product_id,), fetchone=True)
        if not id_level:
            print(f"No product level found for ID: {product_id}")
            return ''

        recommend_id = []
        cate_level = ['v_shape', 'polo', 'clean_text', 'design', 'leather', 'color', 'formal', 'converse', 'loafer', 'hook',
                      'chain']

        for product_f in cat_products:
            f_level = execute_query("SELECT * FROM product_level WHERE product_id=%s", (product_f['id'],), fetchone=True)
            if not f_level:
                continue

            match_score = 0
            if f_level['product_id'] != int(product_id):
                for cat_level in cate_level:
                    if f_level[cat_level] == id_level[cat_level]:
                        match_score += 1
                if match_score == 11:
                    recommend_id.append(f_level['product_id'])

        print('Total recommendation found: ' + str(recommend_id))

        if recommend_id:
            placeholders = ','.join(['%s'] * len(recommend_id))
            query = f'''
                SELECT p.*, 
                       COALESCE(l.likes_count, 0) as likes_count,
                       COALESCE(r.avg_rating, 0) as avg_rating
                FROM products p
                LEFT JOIN (
                    SELECT product_id, COUNT(*) as likes_count 
                    FROM product_likes 
                    GROUP BY product_id
                ) l ON p.id = l.product_id
                LEFT JOIN (
                    SELECT product_id, AVG(rating) as avg_rating 
                    FROM product_reviews 
                    GROUP BY product_id
                ) r ON p.id = r.product_id
                WHERE p.id IN ({placeholders})
            '''
            recommend_list = execute_query(query, recommend_id, fetchall=True)
            return recommend_list, recommend_id, category_matched, product_id
        else:
            return ''
    except Exception as e:
        print(f"Error in content_based_filtering: {e}")
        return ''

# Register error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.before_first_request
def initialize_database():
    try:
        from RetailShop.db_helper import execute_query

        # Check if role column exists in users table
        cursor = mysql.connection.cursor()
        cursor.execute("SHOW COLUMNS FROM users LIKE 'role'")
        role_exists = cursor.fetchone()

        # Add role column if it doesn't exist
        if not role_exists:
            execute_query("ALTER TABLE users ADD COLUMN role INT NOT NULL DEFAULT 1", commit=True)
            # Update existing users to have role=1 (regular users)
            execute_query("UPDATE users SET role=1", commit=True)

        # Check if admin user exists (role=0)
        admin_exists = execute_query("SELECT * FROM users WHERE role=0", fetchall=True)

        if not admin_exists:
            # Create admin user if it doesn't exist
            from passlib.hash import sha256_crypt
            admin_password = sha256_crypt.encrypt("admin123")
            execute_query("INSERT INTO users(name, email, username, password, mobile, role) VALUES(%s, %s, %s, %s, %s, %s)",
                        ("Admin", "admin@example.com", "admin", admin_password, "", 0), commit=True)
            print("Admin user created with username 'admin' and password 'admin123'")

    except Exception as e:
        print(f"Error initializing database: {e}")

from RetailShop import routes

# Import and register the likes_reviews blueprint
from RetailShop.likes_reviews import likes_reviews
app.register_blueprint(likes_reviews)
