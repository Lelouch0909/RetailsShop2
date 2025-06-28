import builtins
import hashlib
import os
import traceback
from math import ceil
import MySQLdb
from flask import render_template, flash, redirect, url_for, session, request, current_app
from passlib.hash import sha256_crypt
import timeit
import datetime
from RetailShop.db_helper import execute_query, get_db, close_db
from RetailShop.form import OrderForm, LoginForm, UpdateRegisterForm, DeveloperForm, MessageForm, RegisterForm, AddToCartForm, CheckoutForm
from RetailShop import app, not_logged_in, is_logged_in, content_based_filtering, wrappers, photos, is_admin_logged_in, \
    not_admin_logged_in, mysql
import pymysql.cursors

# Register close_db function to be called when application context ends
app.teardown_appcontext(close_db)


@app.route('/')
def index():
    form = OrderForm(request.form)
    try:
        # Get products for different categories with likes and ratings
        tshirt_query = """
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
            WHERE p.category = %s
            ORDER BY RAND() 
            LIMIT 4
        """

        tshirt = execute_query(tshirt_query, ('tshirt',), fetchall=True)
        wallet = execute_query(tshirt_query, ('wallet',), fetchall=True)
        belt = execute_query(tshirt_query, ('belt',), fetchall=True)
        shoes = execute_query(tshirt_query, ('shoes',), fetchall=True)

        # Get products for style categories (BROWSE BY DRESS STYLE section) with likes and ratings
        style_query = """
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
            WHERE p.item = %s OR p.category = %s
            ORDER BY RAND() 
            LIMIT 3
        """

        casual_products = execute_query(style_query, ('casual', 'tshirt'), fetchall=True)
        formal_products = execute_query(style_query, ('formal', 'wallet'), fetchall=True)
        party_products = execute_query(style_query, ('party', 'belt'), fetchall=True)
        gym_products = execute_query(style_query, ('gym', 'shoes'), fetchall=True)

        if tshirt is None or wallet is None or belt is None or shoes is None:
            flash('Database error. Please check your database configuration.', 'danger')
            return render_template('modern_home.html', tshirt=[], wallet=[], belt=[], shoes=[], 
                                 casual_products=[], formal_products=[], party_products=[], gym_products=[],
                                 form=form, db_error=True)

        # Handle None values for style products
        casual_products = casual_products or []
        formal_products = formal_products or []
        party_products = party_products or []
        gym_products = gym_products or []

        # Get reviews for testimonials
        testimonials_query = """
            SELECT r.*, u.name as user_name, p.pName as product_name
            FROM product_reviews r
            JOIN users u ON r.user_id = u.id
            JOIN products p ON r.product_id = p.id
            ORDER BY r.rating DESC, r.created_at DESC
            LIMIT 3
        """
        testimonials = execute_query(testimonials_query, (), fetchall=True) or []

        return render_template('modern_home.html', tshirt=tshirt, wallet=wallet, belt=belt, shoes=shoes, 
                             casual_products=casual_products, formal_products=formal_products, 
                             party_products=party_products, gym_products=gym_products,
                             testimonials=testimonials,
                             form=form, db_error=False)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('modern_home.html', tshirt=[], wallet=[], belt=[], shoes=[], 
                             casual_products=[], formal_products=[], party_products=[], gym_products=[],
                             form=form, db_error=True)


# User Login
@app.route('/login', methods=['GET', 'POST'])
@not_logged_in
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            # Get user form
            username = form.username.data
            password_candidate = form.password.data

            # Get user by username
            data = execute_query("SELECT * FROM users WHERE username=%s", (username,), fetchone=True)

            if data:
                # Get stored value
                password = data['password']
                uid = data['id']
                name = data['name']

                # Compare password
                if sha256_crypt.verify(password_candidate, password):
                    # passed
                    session['logged_in'] = True
                    session['uid'] = uid
                    session['s_name'] = name
                    x = '1'
                    execute_query("UPDATE users SET online=%s WHERE id=%s", (x, uid), commit=True)

                    # Check if user is admin (role=0)
                    role = data.get('role')
                    if role == 0:
                        # Set admin session variables
                        session['admin_logged_in'] = True
                        session['admin_uid'] = uid
                        session['admin_name'] = name
                        return redirect(url_for('admin'))

                    return redirect(url_for('index'))

                else:
                    flash('Incorrect password', 'danger')
                    return render_template('login.html', form=form)

            else:
                flash('Username not found', 'danger')
                return render_template('login.html', form=form)
        except Exception as e:
            flash(f'Database error: {str(e)}', 'danger')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/out')
def logout():
    if 'uid' in session:
        try:
            uid = session['uid']
            x = '0'
            execute_query("UPDATE users SET online=%s WHERE id=%s", (x, uid), commit=True)
        except Exception as e:
            print(f"Error updating user online status: {e}")
            # Continue with logout even if database update fails

        session.clear()
        flash('You are logged out', 'success')
        return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
@not_logged_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            name = form.name.data
            email = form.email.data
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))
            mobile = form.mobile.data

            # Insert user into database with role=1 (regular user)
            execute_query("INSERT INTO users(name, email, username, password, mobile, role) VALUES(%s, %s, %s, %s, %s, %s)",
                        (name, email, username, password, mobile, 1), commit=True)

            flash('You are now registered and can login', 'success')

            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Database error: {str(e)}', 'danger')
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)

@app.route('/chatting/<string:id>', methods=['GET', 'POST'])
def chatting(id):
    if 'uid' in session:
        form = MessageForm(request.form)

        # lid name
        l_data = execute_query("SELECT * FROM users WHERE id=%s", [id], fetchone=True)
        if l_data:
            session['name'] = l_data['name']
            uid = session['uid']
            session['lid'] = id

            if request.method == 'POST' and form.validate():
                txt_body = form.body.data
                execute_query("INSERT INTO messages(body, msg_by, msg_to) VALUES(%s, %s, %s)",
                            (txt_body, id, uid), commit=True)

            # Get users
            users = execute_query("SELECT * FROM users", fetchall=True)

            return render_template('chat_room.html', users=users, form=form)
        else:
            flash('No permission!', 'danger')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/chats', methods=['GET', 'POST'])
def chats():
    if 'lid' in session:
        id = session['lid']
        uid = session['uid']
        # Get messages
        chats = execute_query("SELECT * FROM messages WHERE (msg_by=%s AND msg_to=%s) OR (msg_by=%s AND msg_to=%s) "
                    "ORDER BY id ASC", (id, uid, uid, id), fetchall=True)
        return render_template('chats.html', chats=chats)
    return redirect(url_for('login'))

@app.route('/tshirt', methods=['GET', 'POST'])
def tshirt():
    form = OrderForm(request.form)
    # Get products
    values = 'tshirt'
    products = execute_query("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,), fetchall=True)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        if 'uid' in session:
            uid = session['uid']
            execute_query("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place, quantity, now_time), commit=True)
        else:
            execute_query("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place, quantity, now_time), commit=True)

        flash('Order successful', 'success')
        return render_template('tshirt.html', tshirt=products, form=form)

    if 'view' in request.args:
        product_id = request.args['view']
        product = execute_query("SELECT * FROM products WHERE id=%s", (product_id,), fetchall=True)
        x = content_based_filtering(product_id)
        wrappered = wrappers(content_based_filtering, product_id)
        execution_time = timeit.timeit(wrappered, number=0)
        # print('Execution time: ' + str(execution_time) + ' usec')

        if 'uid' in session:
            uid = session['uid']
            result = execute_query("SELECT * FROM product_view WHERE user_id=%s AND product_id=%s", (uid, product_id), fetchall=True)

            if result:
                now = datetime.datetime.now()
                now_time = now.strftime("%y-%m-%d %H:%M:%S")
                execute_query("UPDATE product_view SET date=%s WHERE user_id=%s AND product_id=%s",
                            (now_time, uid, product_id), commit=True)
            else:
                execute_query("INSERT INTO product_view(user_id, product_id) VALUES(%s, %s)", (uid, product_id), commit=True)

        return render_template('view_product.html', x=x, tshirts=product)

    elif 'order' in request.args:
        product_id = request.args['order']
        product = execute_query("SELECT * FROM products WHERE id=%s", (product_id,), fetchall=True)
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, tshirts=product, form=form)

    return render_template('tshirt.html', tshirt=products, form=form)

@app.route('/wallet', methods=['GET', 'POST'])
def wallet():
    form = OrderForm(request.form)
    # Get products
    values = 'wallet'
    products = execute_query("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,), fetchall=True)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']

        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        if 'uid' in session:
            uid = session['uid']
            execute_query("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place, quantity, now_time), commit=True)
        else:
            execute_query("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place, quantity, now_time), commit=True)

        flash('Order successful', 'success')
        return render_template('wallet.html', wallet=products, form=form)

    if 'view' in request.args:
        q = request.args['view']
        product_id = q
        x = content_based_filtering(product_id)
        products = execute_query("SELECT * FROM products WHERE id=%s", (q,), fetchall=True)
        return render_template('view_product.html', x=x, tshirts=products)

    elif 'order' in request.args:
        product_id = request.args['order']
        product = execute_query("SELECT * FROM products WHERE id=%s", (product_id,), fetchall=True)
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, tshirts=product, form=form)

    return render_template('wallet.html', wallet=products, form=form)

@app.route('/belt', methods=['GET', 'POST'])
def belt():
    form = OrderForm(request.form)
    # Get products
    values = 'belt'
    products = execute_query("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,), fetchall=True)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        if 'uid' in session:
            uid = session['uid']
            execute_query("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place, quantity, now_time), commit=True)
        else:
            execute_query("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place, quantity, now_time), commit=True)

        flash('Order successful', 'success')
        return render_template('belt.html', belt=products, form=form)

    if 'view' in request.args:
        q = request.args['view']
        product_id = q
        x = content_based_filtering(product_id)
        products = execute_query("SELECT * FROM products WHERE id=%s", (q,), fetchall=True)
        return render_template('view_product.html', x=x, tshirts=products)

    elif 'order' in request.args:
        product_id = request.args['order']
        product = execute_query("SELECT * FROM products WHERE id=%s", (product_id,), fetchall=True)
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, tshirts=product, form=form)

    return render_template('belt.html', belt=products, form=form)

@app.route('/shoes', methods=['GET', 'POST'])
def shoes():
    form = OrderForm(request.form)
    # Get products
    values = 'shoes'
    products = execute_query("SELECT * FROM products WHERE category=%s ORDER BY id ASC", (values,), fetchall=True)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile_num.data
        order_place = form.order_place.data
        quantity = form.quantity.data
        pid = request.args['order']
        now = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        delivery_date = now + week
        now_time = delivery_date.strftime("%y-%m-%d %H:%M:%S")

        if 'uid' in session:
            uid = session['uid']
            execute_query("INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s, %s)",
                         (uid, pid, name, mobile, order_place, quantity, now_time), commit=True)
        else:
            execute_query("INSERT INTO orders(pid, ofname, mobile, oplace, quantity, ddate) "
                         "VALUES(%s, %s, %s, %s, %s, %s)",
                         (pid, name, mobile, order_place, quantity, now_time), commit=True)

        flash('Order successful', 'success')
        return render_template('shoes.html', shoes=products, form=form)

    if 'view' in request.args:
        q = request.args['view']
        product_id = q
        x = content_based_filtering(product_id)
        products = execute_query("SELECT * FROM products WHERE id=%s", (q,), fetchall=True)
        return render_template('view_product.html', x=x, tshirts=products)

    elif 'order' in request.args:
        product_id = request.args['order']
        product = execute_query("SELECT * FROM products WHERE id=%s", (product_id,), fetchall=True)
        x = content_based_filtering(product_id)
        return render_template('order_product.html', x=x, tshirts=product, form=form)

    return render_template('shoes.html', shoes=products, form=form)



@app.route('/admin_login', methods=['GET', 'POST'])
@not_admin_logged_in
def admin_login():
    if request.method == 'POST':
        # Get user form
        username = request.form['email']
        password_candidate = request.form['password']

        print(f"Admin login attempt with username: {username}")

        try:
            # Get user by username or email
            data = execute_query("SELECT * FROM users WHERE username=%s OR email=%s", [username, username], fetchone=True)

            if data:
                # Get stored value
                password = data['password']
                uid = data['id']
                name = data['name']

                # Check if role column exists
                role = data.get('role')
                print(f"User found: {name} (ID: {uid}), Role: {role}")

                # Check if user is an admin (role=0)
                if role != 0:
                    print(f"User {username} is not an admin (role: {role})")
                    flash('You do not have admin privileges', 'danger')
                    return render_template('pages/login.html')

                # Compare password
                password_match = sha256_crypt.verify(password_candidate, password)
                print(f"Password match: {password_match}")

                if password_match:
                    session['admin_logged_in'] = True
                    session['admin_uid'] = uid
                    session['admin_name'] = name
                    print(f"Admin login successful: {name}")
                    return redirect(url_for('admin'))
                else:
                    flash('Incorrect password', 'danger')
                    return render_template('pages/login.html')
            else:
                print(f"User not found: {username}")
                flash('Username not found', 'danger')
                return render_template('pages/login.html')
        except Exception as e:
            print(f"Error in admin_login: {e}")
            flash(f'An error occurred: {e}', 'danger')
            return render_template('pages/login.html')
    return render_template('pages/login.html')


@app.route('/admin_out')
def admin_logout():
    if 'admin_logged_in' in session:
        session.clear()
        return redirect(url_for('admin_login'))
    return redirect(url_for('admin'))


PER_PAGE = 10
@app.route('/admin')
@is_admin_logged_in
def admin():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE

    # Connexion à la base de données
    cur = mysql.connection.cursor(pymysql.cursors.DictCursor)

    try:
        # Produits (avec pagination)
        # Compte total
        cur.execute("SELECT COUNT(*) as total FROM products")
        total_products = cur.fetchone()['total']
        total_pages = ceil(total_products / PER_PAGE)

        # Données paginées
        cur.execute("SELECT * FROM products ORDER BY id DESC LIMIT %s OFFSET %s", (PER_PAGE, offset))
        products = cur.fetchall()

        # Autres statistiques (sans pagination)
        cur.execute("SELECT COUNT(*) as total FROM users")
        total_users = cur.fetchone()['total']

        cur.execute("SELECT COUNT(*) as total FROM orders")
        total_orders = cur.fetchone()['total']

        return render_template('pages/index.html',
                               result=products,
                               row=total_products,
                               users_rows=total_users,
                               order_rows=total_orders,
                               pagination={
                                   'page': page,
                                   'per_page': PER_PAGE,
                                   'total': total_products,
                                   'total_pages': total_pages
                               }, max=builtins.max,
                                 min=builtins.min)
    finally:
        cur.close()


PER_PAGE = 10
@app.route('/orders')
@is_admin_logged_in
def orders():
    # Pagination
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE

    cur = mysql.connection.cursor(pymysql.cursors.DictCursor)

    try:
        # Comptage total des commandes
        cur.execute("SELECT COUNT(*) as total FROM orders")
        total_orders = cur.fetchone()['total']
        total_pages = ceil(total_orders / PER_PAGE)

        # Commandes paginées
        cur.execute("SELECT * FROM orders ORDER BY odate DESC LIMIT %s OFFSET %s", (PER_PAGE, offset))
        orders = cur.fetchall()

        # Autres statistiques (optionnel)
        cur.execute("SELECT COUNT(*) as total FROM products")
        num_rows = cur.fetchone()['total']

        cur.execute("SELECT COUNT(*) as total FROM users")
        users_rows = cur.fetchone()['total']

        return render_template('pages/all_orders.html',
                               result=orders,
                               row=num_rows,
                               order_rows=total_orders,
                               users_rows=users_rows,
                               pagination={
                                   'page': page,
                                   'per_page': PER_PAGE,
                                   'total': total_orders,
                                   'total_pages': total_pages
                               })
    finally:
        cur.close()

@app.route('/order/<int:order_id>/manage', methods=['GET', 'POST'])
def manage_order(order_id):
    cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
                SELECT o.*,
                       u.name as user_name,
                       u.email as user_email,
                       p.pName as product_name,  
                       p.price as product_price
                FROM orders o
                LEFT JOIN users u ON o.uid = u.id  
                JOIN products p ON o.pid = p.id   
                WHERE o.id = %s
            """, (order_id,))
    order = cursor.fetchone()

    if not order:
        flash("Commande introuvable.", "danger")
        return redirect(url_for('orders'))

    if request.method == 'POST':
        action = request.form.get("action")
        if action == "complete":
            cursor.execute("UPDATE orders SET dstatus = %s WHERE id = %s", ('Traité', order_id))
            mysql.connection.commit()
            flash('Commande marquée comme traitée.', 'success')
        elif action == "cancel":
            cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
            mysql.connection.commit()
            flash('Commande annulée.', 'warning')
        return redirect(url_for('orders'))

    return render_template('pages/manage_order.html', order=order)


@app.route('/users')
@is_admin_logged_in
def users():
    products = execute_query("SELECT * FROM products", fetchall=True)
    num_rows = len(products) if products else 0
    orders = execute_query("SELECT * FROM orders", fetchall=True)
    order_rows = len(orders) if orders else 0
    result = execute_query("SELECT * FROM users", fetchall=True)
    users_rows = len(result) if result else 0
    return render_template('pages/all_users.html', result=result, row=num_rows, order_rows=order_rows,
                           users_rows=users_rows)


@app.route('/admin_add_product', methods=['POST', 'GET'])
@is_admin_logged_in
def admin_add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form['price']
        description = request.form['description']
        available = request.form['available']
        category = request.form['category']
        item = request.form['item']
        code = request.form['code']
        file = request.files['picture']
        if name and price and description and available and category and item and code and file:
            pic = file.filename
            photo = pic.replace("'", "")
            picture = photo.replace(" ", "_")
            if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
                save_photo = photos.save(file, folder=category)
                if save_photo:
                    # Insert product into database
                    product_id = execute_query("INSERT INTO products(pName,price,description,available,category,item,pCode,picture)"
                                 "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                                 (name, price, description, available, category, item, code, picture), commit=True)

                    execute_query("INSERT INTO product_level(product_id) VALUES(%s)", [product_id], commit=True)

                    if category == 'smartphone':
                        level = request.form.getlist('smartphone')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            execute_query(query, (yes, product_id), commit=True)

                    elif category == 'laptop':
                        level = request.form.getlist('laptop')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            execute_query(query, (yes, product_id), commit=True)

                    elif category == 'television':
                        level = request.form.getlist('television')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            execute_query(query, (yes, product_id), commit=True)

                    elif category == 'appliance':
                        level = request.form.getlist('appliance')
                        for lev in level:
                            yes = 'yes'
                            query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                            execute_query(query, (yes, product_id), commit=True)

                    else:
                        flash('Product level not fund', 'danger')
                        return redirect(url_for('admin_add_product'))

                    flash('Product added successful', 'success')
                    return redirect(url_for('admin_add_product'))
                else:
                    flash('Picture not save', 'danger')
                    return redirect(url_for('admin_add_product'))
            else:
                flash('File not supported', 'danger')
                return redirect(url_for('admin_add_product'))
        else:
            flash('Please fill up all form', 'danger')
            return redirect(url_for('admin_add_product'))
    else:
        return render_template('pages/add_product.html')


@app.route('/edit_product', methods=['POST', 'GET'])
@is_admin_logged_in
def edit_product():
    if 'id' in request.args:
        product_id = request.args['id']
        product = execute_query("SELECT * FROM products WHERE id=%s", (product_id,), fetchall=True)
        product_level = execute_query("SELECT * FROM product_level WHERE product_id=%s", (product_id,), fetchall=True)

        if product:
            if request.method == 'POST':
                name = request.form.get('name')
                price = request.form['price']
                description = request.form['description']
                available = request.form['available']
                category = request.form['category']
                item = request.form['item']
                code = request.form['code']
                file = request.files['picture']

                if name and price and description and available and category and item and code and file:
                    pic = file.filename
                    photo = pic.replace("'", "")
                    picture = photo.replace(" ", "")
                    if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
                        file.filename = picture
                        save_photo = photos.save(file, folder=category)
                        if save_photo:
                            # Update product in database
                            exe = execute_query(
                                "UPDATE products SET pName=%s, price=%s, description=%s, available=%s, category=%s, item=%s, pCode=%s, picture=%s WHERE id=%s",
                                (name, price, description, available, category, item, code, picture, product_id), commit=True)

                            if exe is not None:
                                if category == 'smartphone':
                                    level = request.form.getlist('smartphone')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                                        execute_query(query, (yes, product_id), commit=True)

                                elif category == 'laptop':
                                    level = request.form.getlist('laptop')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                                        execute_query(query, (yes, product_id), commit=True)

                                elif category == 'television':
                                    level = request.form.getlist('television')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                                        execute_query(query, (yes, product_id), commit=True)

                                elif category == 'appliance':
                                    level = request.form.getlist('appliance')
                                    for lev in level:
                                        yes = 'yes'
                                        query = 'UPDATE product_level SET {field}=%s WHERE product_id=%s'.format(field=lev)
                                        execute_query(query, (yes, product_id), commit=True)

                                else:
                                    flash('Product level not fund', 'danger')
                                    return redirect(url_for('admin_add_product'))

                                flash('Product updated', 'success')
                                return redirect(url_for('edit_product'))
                            else:
                                flash('Data updated', 'success')
                                return redirect(url_for('edit_product'))
                        else:
                            flash('Pic not upload', 'danger')
                            return render_template('pages/edit_product.html', product=product,
                                                   product_level=product_level)
                    else:
                        flash('File not support', 'danger')
                        return render_template('pages/edit_product.html', product=product,
                                               product_level=product_level)
                else:
                    flash('Fill all field', 'danger')
                    return render_template('pages/edit_product.html', product=product,
                                           product_level=product_level)
            else:
                return render_template('pages/edit_product.html', product=product, product_level=product_level)
        else:
            return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('admin_login'))


@app.route('/search', methods=['POST', 'GET'])
def search():
    form = OrderForm(request.form)
    if 'q' in request.args:
        q = request.args['q']
        # Get products matching search query
        query_string = "SELECT * FROM products WHERE pName LIKE %s ORDER BY id ASC"
        products = execute_query(query_string, ('%' + q + '%',), fetchall=True)
        flash('Showing result for: ' + q, 'success')
        return render_template('search.html', products=products, form=form)
    else:
        flash('Search again', 'danger')
        return render_template('search.html')


app.route('/profile')
@is_logged_in
def profile():
    if 'user' in request.args:
        q = request.args['user']
        curso = mysql.connection.cursor()
        curso.execute("SELECT * FROM users WHERE id=%s", (q,))
        result = curso.fetchone()
        if result:
            if result['id'] == session['uid']:
                curso.execute("SELECT * FROM orders WHERE uid=%s ORDER BY id ASC", (session['uid'],))
                res = curso.fetchall()
                return render_template('profile.html', result=res)
            else:
                flash('Unauthorised', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Unauthorised! Please login', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Unauthorised', 'danger')
        return redirect(url_for('login'))


@app.route('/statistiques')
@is_admin_logged_in
def statistiques():
    cur = mysql.connection.cursor(pymysql.cursors.DictCursor)  # Important pour avoir des dictionnaires
    stats_data = {}

    try:
        # 1. Total Number of Users
        cur.execute("SELECT COUNT(id) FROM users")
        stats_data['total_users'] = cur.fetchone()['COUNT(id)']

        # 2. Total Number of Products
        cur.execute("SELECT COUNT(id) FROM products")
        stats_data['total_products'] = cur.fetchone()['COUNT(id)']

        # 3. Total Number of Orders
        cur.execute("SELECT COUNT(id) FROM orders")
        stats_data['total_orders'] = cur.fetchone()['COUNT(id)']

        # 4. Number of Online Users
        cur.execute("SELECT COUNT(id) FROM users WHERE online = '1'")
        stats_data['online_users'] = cur.fetchone()['COUNT(id)']

        # 5. Orders by Category (for a chart)
        # Assuming products table has 'category' and orders table links to products via 'pid'
        cur.execute("""
            SELECT p.category as label, COUNT(o.id) as value
            FROM orders o
            JOIN products p ON o.pid = p.id
            GROUP BY p.category
            ORDER BY value DESC
        """)
        stats_data['orders_by_category'] = cur.fetchall()

        # 6. Product Distribution - Format adapté pour Morris Donut
        cur.execute("""
            SELECT category as label, COUNT(id) as value
            FROM products
            GROUP BY category
            ORDER BY value DESC
        """)
        stats_data['products_by_category'] = cur.fetchall()

    except Exception as e:
        flash(f'Erreur lors de la récupération des statistiques: {str(e)}', 'danger')
        stats_data = {
            'orders_by_category': [],
            'products_by_category': []
        }
    finally:
        cur.close()

    return render_template('pages/statistics.html', stats=stats_data)


@app.route('/settings', methods=['POST', 'GET'])
@is_logged_in
def settings():
    form = UpdateRegisterForm(request.form)
    if 'user' in request.args:
        q = request.args['user']
        result = execute_query("SELECT * FROM users WHERE id=%s", (q,), fetchone=True)
        if result:
            if result['id'] == session['uid']:
                if request.method == 'POST' and form.validate():
                    name = form.name.data
                    email = form.email.data
                    password = sha256_crypt.encrypt(str(form.password.data))
                    mobile = form.mobile.data

                    # Update user in database
                    exe = execute_query("UPDATE users SET name=%s, email=%s, password=%s, mobile=%s WHERE id=%s",
                                      (name, email, password, mobile, q), commit=True)
                    if exe is not None:
                        flash('Profile updated', 'success')
                        return render_template('user_settings.html', result=result, form=form)
                    else:
                        flash('Profile not updated', 'danger')
                return render_template('user_settings.html', result=result, form=form)
            else:
                flash('Unauthorised', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Unauthorised! Please login', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Unauthorised', 'danger')
        return redirect(url_for('login'))


@app.route('/admin_profile')
@is_admin_logged_in
def admin_profile():
    try:
        cur = mysql.connection.cursor(pymysql.cursors.DictCursor)

        # 1. Récupérer les infos admin
        cur.execute("SELECT * FROM admin WHERE id = %s", [session['admin_id']])
        admin = cur.fetchone()

        if not admin:
            flash('Profil administrateur introuvable', 'danger')
            return redirect(url_for('admin_login'))


        return render_template('pages/admin_profile.html',
                               admin=admin)

    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
        return redirect(url_for('admin'))
    finally:
        if 'cur' in locals():
            cur.close()

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
UPLOAD_FOLDER = os.path.join('static', 'images', 'admin')  # Changé 'image' en 'images'
MAX_FILE_SIZE = 16 * 1024 * 1024
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/update_admin_profile', methods=['GET', 'POST'])
@is_admin_logged_in
def update_admin_profile():
    UPLOAD_FOLDER_ABSOLUTE = os.path.join(current_app.root_path, 'static', 'image', 'admin')

    if request.method == 'GET':
        cur = mysql.connection.cursor(pymysql.cursors.DictCursor)
        try:
            cur.execute("SELECT * FROM admin WHERE id = %s", [session['admin_id']])
            admin = cur.fetchone()
        except Exception as e:
            flash(f"Erreur lors de la récupération du profil: {str(e)}", "danger")
            admin = None
        finally:
            cur.close()

        if not admin:
            flash("Profil administrateur introuvable.", "danger")
            return redirect(url_for('admin_dashboard'))

        return render_template('pages/edit_admin_profile.html', admin=admin)

    if request.method == 'POST':
        cur = None
        try:
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            email = request.form['email']
            mobile = request.form.get('mobile', '')
            address = request.form.get('address', '')
            current_password = request.form['current_password']
            image_file = request.files.get('image')

            if not all([firstName, lastName, email, current_password]):
                flash('Tous les champs obligatoires doivent être remplis.', 'danger')
                return redirect(url_for('update_admin_profile'))

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Fetch only password and image_profile to avoid issues if other columns are missing during initial setup
            cur.execute("SELECT password, image_profile FROM admin WHERE id = %s", [session['admin_id']])
            admin_data = cur.fetchone()

            if not admin_data:
                flash('Administrateur introuvable ou non connecté.', 'danger')
                return redirect(url_for('update_admin_profile'))

            # Vérification du mot de passe (adaptez selon votre méthode de hachage)
            hashed_password = hashlib.sha256(current_password.encode()).hexdigest()
            if hashed_password != admin_data['password']: # Using admin_data here
                flash('Mot de passe actuel incorrect.', 'danger')
                return redirect(url_for('update_admin_profile'))

            image_profile = admin_data.get('image_profile') # Use .get() for safety

            if image_file and image_file.filename != '':
                if not allowed_file(image_file.filename):
                    flash("Format de fichier non autorisé. Formats acceptés : jpg, jpeg, png, gif.", "danger")
                    return redirect(url_for('update_admin_profile'))

                file_ext = os.path.splitext(image_file.filename)[1].lower()
                new_filename = f"admin_{session['admin_id']}{file_ext}"

                # Use the absolute path defined above
                os.makedirs(UPLOAD_FOLDER_ABSOLUTE, exist_ok=True)
                upload_path = os.path.join(UPLOAD_FOLDER_ABSOLUTE, new_filename)

                # --- Debugging Print Statements ---
                print(f"DEBUG: Tentative d'enregistrement de l'image.")
                print(f"DEBUG: Fichier: {image_file.filename}")
                print(f"DEBUG: Chemin absolu du dossier: {UPLOAD_FOLDER_ABSOLUTE}")
                print(f"DEBUG: Chemin complet de sauvegarde: {upload_path}")
                # --- End Debugging Print Statements ---

                try:
                    image_file.save(upload_path)
                    print(f"DEBUG: Image enregistrée avec succès: {upload_path}")

                    # Delete old image if it's not the default one and different from new
                    if image_profile and image_profile != 'default_admin.png' and image_profile != new_filename:
                        old_image_path = os.path.join(UPLOAD_FOLDER_ABSOLUTE, image_profile)
                        if os.path.exists(old_image_path):
                            try:
                                os.remove(old_image_path)
                                print(f"DEBUG: Ancienne image supprimée: {old_image_path}")
                            except OSError as remove_err: # Catch specific OSError for file ops
                                print(f"WARNING: Impossible de supprimer l'ancienne image {old_image_path}: {remove_err}")

                    image_profile = new_filename # Update the filename to store in DB

                except Exception as save_error:
                    print(f"ERREUR CRITIQUE: Erreur lors de l'enregistrement du fichier: {save_error}")
                    print(f"TRACEBACK: {traceback.format_exc()}")
                    flash(f"Impossible d'enregistrer l'image. Vérifiez les permissions du dossier: {str(save_error)}", "danger")
                    return redirect(url_for('update_admin_profile'))
            else:
                print("DEBUG: Pas de fichier image soumis ou fichier vide.")


            # Mise à jour en base de données
            cur.execute("""
                UPDATE admin SET
                    firstName = %s,
                    lastName = %s,
                    email = %s,
                    mobile = %s,
                    address = %s,
                    image_profile = %s
                WHERE id = %s
            """, (firstName, lastName, email, mobile, address, image_profile, session['admin_id']))

            mysql.connection.commit()

            session['admin_name'] = firstName
            session['admin_image'] = image_profile

            flash('Profil mis à jour avec succès.', 'success')

        except Exception as e:
            if cur:
                mysql.connection.rollback()
            flash(f'Une erreur est survenue lors de la mise à jour du profil : {str(e)}', 'danger')
            print(f"Erreur générale de mise à jour: {traceback.format_exc()}")
        finally:
            if cur:
                cur.close()

        return redirect(url_for('admin_profile'))



@app.route('/developer', methods=['POST', 'GET'])
def developer():
    form = DeveloperForm(request.form)
    if request.method == 'POST' and form.validate():
        q = form.id.data
        product = execute_query("SELECT * FROM products WHERE id=%s", (q,), fetchone=True)
        if product:
            x = content_based_filtering(q)
            wrappered = wrappers(content_based_filtering, q)
            execution_time = timeit.timeit(wrappered, number=0)
            seconds = ((execution_time / 1000) % 60)
            return render_template('developer.html', form=form, x=x, execution_time=seconds)
        else:
            nothing = 'Nothing found'
            return render_template('developer.html', form=form, nothing=nothing)
    else:
        return render_template('developer.html', form=form)

# Modern interface route
@app.route('/modern')
def modern_index():
    form = OrderForm(request.form)
    try:
        # Get products for different categories with likes and ratings
        product_query = """
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
            WHERE p.category = %s
            ORDER BY RAND() 
            LIMIT 4
        """

        tshirt = execute_query(product_query, ('tshirt',), fetchall=True)
        wallet = execute_query(product_query, ('wallet',), fetchall=True)
        belt = execute_query(product_query, ('belt',), fetchall=True)
        shoes = execute_query(product_query, ('shoes',), fetchall=True)

        if tshirt is None or wallet is None or belt is None or shoes is None:
            flash('Database error. Please check your database configuration.', 'danger')
            return render_template('modern_home.html', tshirt=[], wallet=[], belt=[], shoes=[], form=form, db_error=True)

        # Get reviews for testimonials
        testimonials_query = """
            SELECT r.*, u.name as user_name, p.pName as product_name
            FROM product_reviews r
            JOIN users u ON r.user_id = u.id
            JOIN products p ON r.product_id = p.id
            ORDER BY r.rating DESC, r.created_at DESC
            LIMIT 3
        """
        testimonials = execute_query(testimonials_query, (), fetchall=True) or []

        return render_template('modern_home.html', tshirt=tshirt, wallet=wallet, belt=belt, shoes=shoes, 
                             testimonials=testimonials, form=form, db_error=False)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('modern_home.html', tshirt=[], wallet=[], belt=[], shoes=[], form=form, db_error=True)

# Old interface route for comparison
@app.route('/old')
def old_index():
    form = OrderForm(request.form)
    try:
        # Get products for different categories with likes and ratings
        product_query = """
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
            WHERE p.category = %s
            ORDER BY RAND() 
            LIMIT 4
        """

        tshirt = execute_query(product_query, ('tshirt',), fetchall=True)
        wallet = execute_query(product_query, ('wallet',), fetchall=True)
        belt = execute_query(product_query, ('belt',), fetchall=True)
        shoes = execute_query(product_query, ('shoes',), fetchall=True)

        if tshirt is None or wallet is None or belt is None or shoes is None:
            flash('Database error. Please check your database configuration.', 'danger')
            return render_template('home.html', tshirt=[], wallet=[], belt=[], shoes=[], form=form, db_error=True)

        return render_template('home.html', tshirt=tshirt, wallet=wallet, belt=belt, shoes=shoes, form=form, db_error=False)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return render_template('home.html', tshirt=[], wallet=[], belt=[], shoes=[], form=form, db_error=True)


# Cart routes
@app.route('/cart')
@is_logged_in
def cart():
    try:
        # First, ensure cart table exists
        execute_query("""
            CREATE TABLE IF NOT EXISTS cart (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_product (user_id, product_id)
            )
        """, (), commit=True)

        # Get all items in the user's cart
        cart_items = execute_query("""
            SELECT c.id, c.quantity, p.id as product_id, p.pName, p.price, p.picture, p.available
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (session['uid'],), fetchall=True)

        # Handle case where cart_items is None
        if cart_items is None:
            cart_items = []

        # Calculate total price
        total = 0
        for item in cart_items:
            total += item['price'] * item['quantity']

        return render_template('cart.html', cart_items=cart_items, total=total)

    except Exception as e:
        flash(f'Erreur lors du chargement du panier: {str(e)}', 'danger')
        return render_template('cart.html', cart_items=[], total=0)

@app.route('/add_to_cart', methods=['POST'])
@is_logged_in
def add_to_cart():
    form = AddToCartForm(request.form)
    if form.validate():
        product_id = form.product_id.data
        quantity = form.quantity.data

        # Check if product exists and is available
        product = execute_query("SELECT * FROM products WHERE id = %s", (product_id,), fetchone=True)
        if not product:
            flash("Produit non trouvé", "danger")
            return redirect(request.referrer or url_for('index'))

        if product['available'] < int(quantity):
            flash("Quantité non disponible", "danger")
            return redirect(request.referrer or url_for('index'))

        # Check if product is already in cart
        existing_item = execute_query(
            "SELECT * FROM cart WHERE user_id = %s AND product_id = %s", 
            (session['uid'], product_id), 
            fetchone=True
        )

        if existing_item:
            # Update quantity
            new_quantity = existing_item['quantity'] + int(quantity)
            if new_quantity > product['available']:
                flash("Quantité non disponible", "danger")
                return redirect(request.referrer or url_for('index'))

            execute_query(
                "UPDATE cart SET quantity = %s WHERE id = %s",
                (new_quantity, existing_item['id']),
                commit=True
            )
            flash("Quantité mise à jour dans le panier", "success")
        else:
            # Add new item to cart
            execute_query(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                (session['uid'], product_id, quantity),
                commit=True
            )
            flash("Produit ajouté au panier", "success")

        return redirect(request.referrer or url_for('index'))

    flash("Erreur lors de l'ajout au panier", "danger")
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_from_cart/<int:cart_id>')
@is_logged_in
def remove_from_cart(cart_id):
    # Check if cart item belongs to user
    cart_item = execute_query(
        "SELECT * FROM cart WHERE id = %s AND user_id = %s", 
        (cart_id, session['uid']), 
        fetchone=True
    )

    if not cart_item:
        flash("Article non trouvé dans votre panier", "danger")
        return redirect(url_for('cart'))

    # Remove item from cart
    execute_query("DELETE FROM cart WHERE id = %s", (cart_id,), commit=True)
    flash("Article supprimé du panier", "success")
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@is_logged_in
def checkout():
    form = CheckoutForm(request.form)

    # Get cart items
    cart_items = execute_query("""
        SELECT c.id, c.quantity, p.id as product_id, p.pName, p.price, p.picture, p.available
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (session['uid'],), fetchall=True)

    if not cart_items:
        flash("Votre panier est vide", "danger")
        return redirect(url_for('cart'))

    # Calculate total price
    total = 0
    for item in cart_items:
        total += item['price'] * item['quantity']

    if request.method == 'POST' and form.validate():
        name = form.name.data
        mobile = form.mobile.data
        address = form.address.data

        # Create orders for each cart item
        for item in cart_items:
            # Check if product is still available
            product = execute_query("SELECT * FROM products WHERE id = %s", (item['product_id'],), fetchone=True)
            if not product or product['available'] < item['quantity']:
                flash(f"Le produit {item['pName']} n'est plus disponible en quantité suffisante", "danger")
                return redirect(url_for('cart'))

            # Create order
            execute_query("""
                INSERT INTO orders (uid, ofname, pid, quantity, oplace, mobile, dstatus)
                VALUES (%s, %s, %s, %s, %s, %s, 'no')
            """, (session['uid'], name, item['product_id'], item['quantity'], address, mobile), commit=True)

            # Update product availability
            new_available = product['available'] - item['quantity']
            execute_query(
                "UPDATE products SET available = %s WHERE id = %s",
                (new_available, item['product_id']),
                commit=True
            )

        # Clear cart
        execute_query("DELETE FROM cart WHERE user_id = %s", (session['uid'],), commit=True)

        flash("Commande passée avec succès", "success")
        return redirect(url_for('orders'))

    return render_template('checkout.html', form=form, cart_items=cart_items, total=total)

# Category routes
@app.route('/mens')
def mens():
    form = OrderForm(request.form)
    products = execute_query("SELECT * FROM products WHERE category IN ('tshirt', 'wallet', 'belt', 'shoes') AND item='mens'", (), fetchall=True)
    return render_template('category.html', products=products, form=form, category="Hommes")

@app.route('/womens')
def womens():
    form = OrderForm(request.form)
    products = execute_query("SELECT * FROM products WHERE category IN ('tshirt', 'wallet', 'belt', 'shoes') AND item='womens'", (), fetchall=True)
    return render_template('category.html', products=products, form=form, category="Femmes")

@app.route('/arrivals')
def arrivals():
    form = OrderForm(request.form)
    products = execute_query("SELECT * FROM products ORDER BY date DESC LIMIT 8", (), fetchall=True)
    return render_template('category.html', products=products, form=form, category="Nouveautés")

@app.route('/new-arrivals')
def new_arrivals():
    # Redirect to the new route for backward compatibility
    return redirect(url_for('arrivals'))

@app.route('/sales')
def sales():
    form = OrderForm(request.form)
    # Get best-selling products based on order quantity
    products = execute_query("""
        SELECT p.*, COUNT(o.id) as order_count 
        FROM products p
        JOIN orders o ON p.id = o.pid
        GROUP BY p.id
        ORDER BY order_count DESC
        LIMIT 8
    """, (), fetchall=True)

    # Fallback if no orders exist
    if not products:
        products = execute_query("SELECT * FROM products ORDER BY RAND() LIMIT 8", (), fetchall=True)

    return render_template('category.html', products=products, form=form, category="Meilleures Ventes")

@app.route('/view_product/<int:product_id>')
def view_product(product_id):
    # Get product details with likes and ratings
    product_query = """
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
        WHERE p.id = %s
    """

    product = execute_query(product_query, (product_id,), fetchone=True)

    if not product:
        flash('Produit non trouvé', 'danger')
        return redirect(url_for('index'))

    # Get similar products using content-based filtering
    x = content_based_filtering(product_id)

    # Record view if user is logged in
    if 'uid' in session:
        uid = session['uid']
        result = execute_query("SELECT * FROM product_view WHERE user_id=%s AND product_id=%s", 
                             (uid, product_id), fetchall=True)

        if result:
            now = datetime.datetime.now()
            now_time = now.strftime("%y-%m-%d %H:%M:%S")
            execute_query("UPDATE product_view SET date=%s WHERE user_id=%s AND product_id=%s",
                        (now_time, uid, product_id), commit=True)
        else:
            execute_query("INSERT INTO product_view(user_id, product_id) VALUES(%s, %s)", 
                        (uid, product_id), commit=True)

    form = OrderForm(request.form)
    # Template expects 'tshirts' for the main product (as a list) and 'x' for similar products
    return render_template('view_product.html', tshirts=[product], x=x, form=form)

@app.route('/all-products')
def all_products():
    form = OrderForm(request.form)
    category = request.args.get('category', None)

    if category:
        products = execute_query("SELECT * FROM products WHERE category=%s ORDER BY id ASC", 
                               (category,), fetchall=True)
        category_title = category.capitalize()
    else:
        products = execute_query("SELECT * FROM products ORDER BY id ASC", (), fetchall=True)
        category_title = "Tous les produits"

    return render_template('category.html', products=products, form=form, category=category_title)

@app.route('/brands')
def brands():
    form = OrderForm(request.form)
    # This is a placeholder - in a real app, you'd have brand information in the database
    products = execute_query("SELECT * FROM products ORDER BY RAND() LIMIT 8", (), fetchall=True)
    return render_template('category.html', products=products, form=form, category="Marques")

@app.route('/admin_search', methods=['GET', 'POST'])
@is_admin_logged_in
def admin_search():
    if request.method == 'GET' and request.args.get('q'):
        query = request.args.get('q', '').strip()
        if query:
            # Search in products
            products = execute_query(
                "SELECT * FROM products WHERE pName LIKE %s OR category LIKE %s OR description LIKE %s", 
                (f'%{query}%', f'%{query}%', f'%{query}%'), 
                fetchall=True
            )
            # Search in users
            users = execute_query(
                "SELECT * FROM users WHERE name LIKE %s OR email LIKE %s OR username LIKE %s", 
                (f'%{query}%', f'%{query}%', f'%{query}%'), 
                fetchall=True
            )
            # Search in orders
            orders = execute_query(
                "SELECT * FROM orders WHERE ofname LIKE %s OR oplace LIKE %s", 
                (f'%{query}%', f'%{query}%'), 
                fetchall=True
            )

            return render_template('pages/search_results.html', 
                                 products=products or [], 
                                 users=users or [], 
                                 orders=orders or [], 
                                 search_term=query)
        else:
            flash('Veuillez entrer un terme de recherche', 'warning')
            return redirect(url_for('admin'))

    return redirect(url_for('admin'))
