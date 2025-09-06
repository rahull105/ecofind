from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Product
import os
from werkzeug.utils import secure_filename
import config

app = Flask(__name__)
app.config.from_object('config')

mysql = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
UPLOAD_FOLDER = os.path.join('static', 'products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- User Loader for Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(*user)
    return None

# --- Home redirects to Feed ---
@app.route('/')
def home():
    return redirect(url_for('feed'))

# --- User Registration ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO user (email, username, password) VALUES (%s, %s, %s)", (email, username, password))
            mysql.connection.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))
        except:
            flash("Email or username already exists.", "danger")
        finally:
            cur.close()
    return render_template('signup.html')

# --- User Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user[3], password):
            user_obj = User(*user)
            login_user(user_obj)
            return redirect(url_for('feed'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

# --- User Logout ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- User Dashboard/Profile Edit ---
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        username = request.form['username']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE user SET username=%s WHERE id=%s", (username, current_user.id))
        mysql.connection.commit()
        cur.close()
        flash("Profile updated.", "success")
    return render_template('dashboard.html', user=current_user)

# --- Add Product Listing ---
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('static', 'products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    categories = ['Clothing', 'Electronics', 'Books', 'Home', 'Other']
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        description = request.form['description']
        price = request.form['price']

        image = 'placeholder.png'
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{title}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image = f"products/{filename}"  # <--- Note: this IS NOT 'static/products/filename.jpg'

        # Save 'image' variable (which is like 'products/filename.jpg') in the DB
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO product (title, description, category, price, image, owner_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (title, description, category, price, image, current_user.id)
        )
        mysql.connection.commit()
        cur.close()
        flash("Product listed!", "success")
        return redirect(url_for('my_listings'))
    return render_template('add_product.html', categories=categories)
# --- Product Listing Feed (with search/filter) ---
@app.route('/feed')
def feed():
    cur = mysql.connection.cursor()
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = "SELECT * FROM product"
    filters = []
    params = []

    if category:
        filters.append("category=%s")
        params.append(category)
    if search:
        filters.append("title LIKE %s")
        params.append(f"%{search}%")
    if filters:
        query += " WHERE " + " AND ".join(filters)
    cur.execute(query, tuple(params))
    products = cur.fetchall()
    cur.close()
    categories = ['Clothing', 'Electronics', 'Books', 'Home', 'Other']
    return render_template('feed.html', products=products, categories=categories)

# --- My Listings CRUD ---
@app.route('/my_listings')
@login_required
def my_listings():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE owner_id=%s", (current_user.id,))
    products = cur.fetchall()
    cur.close()
    return render_template('my_listings.html', products=products)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE id=%s AND owner_id=%s", (product_id, current_user.id))
    product = cur.fetchone()
    if not product:
        flash("Not authorized.", "danger")
        return redirect(url_for('my_listings'))
    categories = ['Clothing', 'Electronics', 'Books', 'Home', 'Other']
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        description = request.form['description']
        price = request.form['price']
        cur.execute("UPDATE product SET title=%s, category=%s, description=%s, price=%s WHERE id=%s",
                    (title, category, description, price, product_id))
        mysql.connection.commit()
        cur.close()
        flash("Product updated.", "success")
        return redirect(url_for('my_listings'))
    cur.close()
    return render_template('add_product.html', categories=categories, product=product, edit=True)

@app.route('/delete_product/<int:product_id>')
@login_required
def delete_product(product_id):
    cur = mysql.connection.cursor()
    # Remove purchases referencing this product first
    cur.execute("DELETE FROM purchase WHERE product_id=%s", (product_id,))
    # Now remove from cart (optional but safe)
    cur.execute("DELETE FROM cart WHERE product_id=%s", (product_id,))
    # Now delete the product
    cur.execute("DELETE FROM product WHERE id=%s AND owner_id=%s", (product_id, current_user.id))
    mysql.connection.commit()
    cur.close()
    flash("Product deleted.", "success")
    return redirect(url_for('my_listings'))
# --- Product Detail View ---
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE id=%s", (product_id,))
    product = cur.fetchone()
    cur.close()
    return render_template('product_detail.html', product=product)

# --- Add to Cart ---
@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT owner_id FROM product WHERE id=%s", (product_id,))
    owner = cur.fetchone()
    if owner and owner[0] == current_user.id:
        flash("You cannot add your own product to the cart.", "danger")
        cur.close()
        return redirect(url_for('feed'))
    cur.execute("SELECT * FROM cart WHERE user_id=%s AND product_id=%s", (current_user.id, product_id))
    if not cur.fetchone():
        cur.execute("INSERT INTO cart (user_id, product_id) VALUES (%s, %s)", (current_user.id, product_id))
        mysql.connection.commit()
    cur.close()
    flash("Added to cart.", "success")
    return redirect(url_for('cart'))
# --- Cart View ---
@app.route('/cart')
@login_required
def cart():
    cur = mysql.connection.cursor()
    cur.execute("SELECT product.* FROM cart JOIN product ON cart.product_id=product.id WHERE cart.user_id=%s", (current_user.id,))
    products = cur.fetchall()
    cur.close()
    return render_template('cart.html', products=products)

# --- Remove from Cart ---
@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cart WHERE user_id=%s AND product_id=%s", (current_user.id, product_id))
    mysql.connection.commit()
    cur.close()
    flash("Removed from cart.", "success")
    return redirect(url_for('cart'))

# --- Purchase (simulate checkout) ---
@app.route('/purchase')
@login_required
def purchase():
    cur = mysql.connection.cursor()
    cur.execute("SELECT product_id FROM cart WHERE user_id=%s", (current_user.id,))
    items = cur.fetchall()
    for (product_id,) in items:
        cur.execute("INSERT INTO purchase (user_id, product_id) VALUES (%s, %s)", (current_user.id, product_id))
    cur.execute("DELETE FROM cart WHERE user_id=%s", (current_user.id,))
    mysql.connection.commit()
    cur.close()
    flash("Purchase complete!", "success")
    return redirect(url_for('previous_purchase'))

# --- Previous Purchases View ---
@app.route('/previous_purchase')
@login_required
def previous_purchase():
    cur = mysql.connection.cursor()
    cur.execute("SELECT product.* FROM purchase JOIN product ON purchase.product_id=product.id WHERE purchase.user_id=%s", (current_user.id,))
    products = cur.fetchall()
    cur.close()
    return render_template('previous_purchase.html', products=products)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)