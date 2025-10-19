from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

app = Flask(_name_)
app.config['SECRET_KEY'] = 'fashion-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fashion_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Men, Women, Kids
    size = db.Column(db.String(50))  # S, M, L, XL
    color = db.Column(db.String(50))
    stock = db.Column(db.Integer, default=10)
    image = db.Column(db.String(300))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float)
    status = db.Column(db.String(20), default='Processing')
    items = db.Column(db.Text)
    shipping_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Fashion Store{% endblock %}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Helvetica Neue', Arial, sans-serif; 
            background: #f8f9fa;
        }
        
        /* Navigation */
        nav { 
            background: #000; 
            padding: 1rem 3rem; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        nav .logo { 
            color: #fff; 
            font-size: 28px; 
            font-weight: 900; 
            text-decoration: none;
            letter-spacing: 2px;
        }
        nav .menu { display: flex; gap: 30px; align-items: center; }
        nav a { 
            color: #fff; 
            text-decoration: none; 
            padding: 8px 16px; 
            transition: all 0.3s;
            font-weight: 500;
        }
        nav a:hover { color: #ffd700; }
        
        /* Container */
        .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
        
        /* Flash Messages */
        .flash { 
            padding: 15px 20px; 
            margin: 20px 0; 
            border-radius: 5px; 
            animation: slideDown 0.3s ease;
        }
        .flash.success { background: #d4edda; color: #155724; border-left: 5px solid #28a745; }
        .flash.error { background: #f8d7da; color: #721c24; border-left: 5px solid #dc3545; }
        
        @keyframes slideDown { 
            from { opacity: 0; transform: translateY(-20px); } 
            to { opacity: 1; transform: translateY(0); } 
        }
        
        /* Hero Section */
        .hero { 
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                        url('https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?w=1200');
            background-size: cover;
            background-position: center;
            color: white;
            text-align: center;
            padding: 120px 20px;
            margin-bottom: 50px;
        }
        .hero h1 { 
            font-size: 56px; 
            margin-bottom: 20px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 3px;
        }
        .hero p { font-size: 22px; margin-bottom: 30px; }
        
        /* Category Filter */
        .filter-bar {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .filter-btn {
            padding: 10px 25px;
            border: 2px solid #000;
            background: white;
            cursor: pointer;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .filter-btn:hover, .filter-btn.active {
            background: #000;
            color: white;
        }
        
        /* Product Grid */
        .products { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 30px;
        }
        
        .product-card { 
            background: white; 
            border-radius: 10px; 
            overflow: hidden;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        .product-card:hover { 
            transform: translateY(-8px); 
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .product-card img { 
            width: 100%; 
            height: 400px; 
            object-fit: cover;
        }
        .product-card .content { padding: 20px; }
        .product-card h3 { 
            color: #333; 
            margin-bottom: 10px; 
            font-size: 22px;
            font-weight: 700;
        }
        .product-card .category {
            display: inline-block;
            background: #000;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            margin-bottom: 10px;
            font-weight: 600;
        }
        .product-card p { 
            color: #666; 
            margin-bottom: 15px; 
            font-size: 14px;
            line-height: 1.6;
        }
        .product-card .price { 
            color: #000; 
            font-size: 28px; 
            font-weight: 900; 
            margin-bottom: 10px;
        }
        .product-card .details {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 13px;
            color: #666;
        }
        .product-card .size-badge, .product-card .color-badge {
            padding: 5px 12px;
            background: #f1f1f1;
            border-radius: 5px;
            font-weight: 600;
        }
        
        /* Buttons */
        button, .btn { 
            background: #000; 
            color: white; 
            border: none; 
            padding: 15px 35px; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px; 
            font-weight: 700;
            transition: all 0.3s; 
            text-decoration: none; 
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        button:hover, .btn:hover { 
            background: #333;
            transform: scale(1.05);
        }
        button:disabled { 
            opacity: 0.5; 
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .btn-success { background: #28a745; }
        .btn-success:hover { background: #218838; }
        
        /* Forms */
        .card { 
            background: white; 
            border-radius: 10px; 
            padding: 40px; 
            box-shadow: 0 3px 20px rgba(0,0,0,0.1); 
            max-width: 500px;
            margin: 50px auto;
        }
        
        form { width: 100%; }
        .form-group { margin-bottom: 25px; }
        label { 
            display: block; 
            margin-bottom: 8px; 
            color: #333; 
            font-weight: 600;
        }
        input, textarea, select { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 5px; 
            font-size: 14px;
            transition: border 0.3s;
        }
        input:focus, textarea:focus, select:focus { 
            outline: none; 
            border-color: #000;
        }
        
        /* Cart */
        .cart-icon { position: relative; }
        .cart-count { 
            position: absolute; 
            top: -8px; 
            right: -8px; 
            background: #ffd700; 
            color: #000; 
            border-radius: 50%; 
            padding: 4px 8px; 
            font-size: 12px; 
            font-weight: bold;
        }
        
        /* Table */
        table { 
            width: 100%; 
            border-collapse: collapse; 
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        th, td { padding: 18px; text-align: left; }
        th { 
            background: #000; 
            color: white; 
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        tr:nth-child(even) { background: #f8f9fa; }
        tr:hover { background: #e9ecef; }
        
        .empty-state { 
            text-align: center; 
            padding: 80px 20px;
        }
        .empty-state h2 { 
            font-size: 32px; 
            margin-bottom: 15px;
            color: #333;
        }
        .empty-state p { 
            font-size: 18px; 
            color: #666;
            margin-bottom: 30px;
        }
        
        h1, h2 { 
            color: #333; 
            margin-bottom: 30px;
            font-weight: 900;
        }
        
        /* Footer */
        footer {
            background: #000;
            color: white;
            text-align: center;
            padding: 30px;
            margin-top: 50px;
        }
    </style>
</head>
<body>
    <nav>
        <a href="/" class="logo">👔 FASHION STORE</a>
        <div class="menu">
            <a href="/">Home</a>
            <a href="/products">Shop</a>
            <a href="/products?category=Men">Men</a>
            <a href="/products?category=Women">Women</a>
            <a href="/products?category=Kids">Kids</a>
            {% if session.get('user_id') %}
                <a href="/cart" class="cart-icon">
                    🛒 Cart
                    {% if session.get('cart') %}
                        <span class="cart-count">{{ session['cart']|length }}</span>
                    {% endif %}
                </a>
                <a href="/orders">Orders</a>
                {% if session.get('is_admin') %}
                    <a href="/admin">Admin</a>
                {% endif %}
                <a href="/logout">Logout</a>
            {% else %}
                <a href="/login">Login</a>
                <a href="/register">Register</a>
            {% endif %}
        </div>
    </nav>
    
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <footer>
        <p>&copy; 2024 Fashion Store. All Rights Reserved.</p>
    </footer>
</body>
</html>
"""

HOME_PAGE = BASE_HTML.replace('{% block content %}{% endblock %}', """
    <div class="hero">
        <h1>✨ NEW COLLECTION ✨</h1>
        <p>Discover the latest trends in fashion</p>
        <a href="/products" class="btn">Shop Now</a>
    </div>
    
    <h2 style="text-align: center; font-size: 36px;">Featured Items</h2>
    <div class="products">
        {% for product in products[:6] %}
        <div class="product-card">
            <img src="{{ product.image }}" alt="{{ product.name }}">
            <div class="content">
                <span class="category">{{ product.category }}</span>
                <h3>{{ product.name }}</h3>
                <div class="details">
                    <span class="size-badge">Size: {{ product.size }}</span>
                    <span class="color-badge">{{ product.color }}</span>
                </div>
                <div class="price">₹{{ product.price }}</div>
                <a href="/products" class="btn">View All</a>
            </div>
        </div>
        {% endfor %}
    </div>
""")

PRODUCTS_PAGE = BASE_HTML.replace('{% block content %}{% endblock %}', """
    <h1 style="text-align: center; font-size: 42px;">Shop All Products</h1>
    
    <div class="filter-bar">
        <a href="/products"><button class="filter-btn {% if not category %}active{% endif %}">All</button></a>
        <a href="/products?category=Men"><button class="filter-btn {% if category == 'Men' %}active{% endif %}">Men</button></a>
        <a href="/products?category=Women"><button class="filter-btn {% if category == 'Women' %}active{% endif %}">Women</button></a>
        <a href="/products?category=Kids"><button class="filter-btn {% if category == 'Kids' %}active{% endif %}">Kids</button></a>
    </div>
    
    <div class="products">
        {% for product in products %}
        <div class="product-card">
            <img src="{{ product.image }}" alt="{{ product.name }}">
            <div class="content">
                <span class="category">{{ product.category }}</span>
                <h3>{{ product.name }}</h3>
                <p>{{ product.description }}</p>
                <div class="details">
                    <span class="size-badge">Size: {{ product.size }}</span>
                    <span class="color-badge">{{ product.color }}</span>
                    <span style="color: #666;">Stock: {{ product.stock }}</span>
                </div>
                <div class="price">₹{{ product.price }}</div>
                {% if session.get('user_id') %}
                    {% if product.stock > 0 %}
                        <form action="/add_to_cart/{{ product.id }}" method="POST">
                            <button type="submit">Add to Cart</button>
                        </form>
                    {% else %}
                        <button disabled>Out of Stock</button>
                    {% endif %}
                {% else %}
                    <a href="/login" class="btn">Login to Buy</a>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
""")

LOGIN_PAGE = BASE_HTML.replace('{% block content %}{% endblock %}', """
    <div class="card">
        <h2 style="text-align: center;">Welcome Back!</h2>
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" style="width: 100%;">Login</button>
        </form>
        <p style="text-align: center; margin-top: 20px; color: #666;">
            New here? <a href="/register" style="color: #000; font-weight: 600;">Create Account</a>
        </p>
    </div>
""")

REGISTER_PAGE = BASE_HTML.replace('{% block content %}{% endblock %}', """
    <div class="card">
        <h2 style="text-align: center;">Create Account</h2>
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" style="width: 100%;">Register</button>
        </form>
        <p style="text-align: center; margin-top: 20px; color: #666;">
            Already have an account? <a href="/login" style="color: #000; font-weight: 600;">Login</a>
        </p>
    </div>
""")

CART_PAGE = BASE_HTML.replace('{% block content %}{% endblock %}', """
    <h1>Shopping Cart</h1>
    {% if cart_items %}
        <div style="background: white; padding: 30px; border-radius: 10px;">
            <table>
                <tr>
                    <th>Product</th>
                    <th>Size</th>
                    <th>Color</th>
                    <th>Price</th>
                    <th>Quantity</th>
                    <th>Total</th>
                    <th>Action</th>
                </tr>
                {% for item in cart_items %}
                <tr>
                    <td><strong>{{ item.name }}</strong></td>
                    <td>{{ item.size }}</td>
                    <td>{{ item.color }}</td>
                    <td>₹{{ item.price }}</td>
                    <td>{{ item.quantity }}</td>
                    <td><strong>₹{{ item.price * item.quantity }}</strong></td>
                    <td>
                        <form action="/remove_from_cart/{{ item.id }}" method="POST">
                            <button type="submit" class="btn-danger">Remove</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
            <div style="text-align: right; margin-top: 30px; font-size: 32px; font-weight: 900;">
                Total: ₹{{ total }}
            </div>
            <div style="text-align: right; margin-top: 20px;">
                <form action="/checkout" method="POST">
                    <div class="form-group" style="text-align: left; max-width: 400px; margin-left: auto;">
                        <label>Shipping Address</label>
                        <textarea name="address" rows="3" required placeholder="Enter your complete address"></textarea>
                    </div>
                    <button type="submit" class="btn-success" style="font-size: 18px; padding: 18px 50px;">
                        Place Order
                    </button>
                </form>
            </div>
        </div>
    {% else %}
        <div class="empty-state">
            <h2>Your Cart is Empty</h2>
            <p>Start shopping and add items to your cart!</p>
            <a href="/products" class="btn">Start Shopping</a>
        </div>
    {% endif %}
""")

ORDERS_PAGE = BASE_HTML.replace('{% block content %}{% endblock %}', """
    <h1>My Orders</h1>
    {% if orders %}
        {% for order in orders %}
        <div style="background: white; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0;">Order #{{ order.id }}</h3>
                <span style="background: {% if order.status == 'Delivered' %}#28a745{% elif order.status == 'Shipped' %}#ffc107{% else %}#6c757d{% endif %}; color: white; padding: 8px 20px; border-radius: 20px; font-weight: 600;">
                    {{ order.status }}
                </span>
            </div>
            <p><strong>Date:</strong> {{ order.created_at.strftime('%d %B %Y, %I:%M %p') }}</p>
            <p><strong>Shipping Address:</strong> {{ order.shipping_address }}</p>
            <p><strong>Items:</strong></p>
            <ul style="margin-left: 20px; margin-top: 10px;">
                {% for item in order.items_list %}
                    <li style="margin-bottom: 8px;">
                        <strong>{{ item.name }}</strong> - Size: {{ item.size }}, Color: {{ item.color }} - ₹{{ item.price }} x {{ item.quantity }}
                    </li>
                {% endfor %}
            </ul>
            <div style="text-align: right; margin-top: 20px; font-size: 24px; font-weight: 900;">
                Total: ₹{{ order.total }}
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div class="empty-state">
            <h2>No Orders Yet!</h2>
            <p>Place your first order now.</p>
            <a href="/products" class="btn">Start Shopping</a>
        </div>
    {% endif %}
""")

ADMIN_PAGE = BASE_HTML.replace('{% block content %}{% endblock %}', """
    <h1>Admin Panel</h1>
    
    <div style="background: white; padding: 40px; border-radius: 10px; margin-bottom: 30px;">
        <h2>Add New Product</h2>
        <form method="POST" action="/admin/add_product">
            <div class="form-group">
                <label>Product Name</label>
                <input type="text" name="name" required>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="form-group">
                    <label>Price (₹)</label>
                    <input type="number" step="0.01" name="price" required>
                </div>
                <div class="form-group">
                    <label>Stock</label>
                    <input type="number" name="stock" required>
                </div>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="description" rows="3" required></textarea>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
                <div class="form-group">
                    <label>Category</label>
                    <select name="category" required>
                        <option value="Men">Men</option>
                        <option value="Women">Women</option>
                        <option value="Kids">Kids</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Size</label>
                    <select name="size" required>
                        <option value="S">S</option>
                        <option value="M">M</option>
                        <option value="L">L</option>
                        <option value="XL">XL</option>
                        <option value="XXL">XXL</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Color</label>
                    <input type="text" name="color" required placeholder="e.g., Black, Blue">
                </div>
            </div>
            <div class="form-group">
                <label>Image URL</label>
                <input type="text" name="image" required placeholder="https://example.com/image.jpg">
            </div>
            <button type="submit">Add Product</button>
        </form>
    </div>
    
    <div style="background: white; padding: 40px; border-radius: 10px; margin-bottom: 30px;">
        <h2>All Orders</h2>
        <table>
            <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Total</th>
                <th>Status</th>
                <th>Date</th>
                <th>Action</th>
            </tr>
            {% for order in orders %}
            <tr>
                <td>#{{ order.id }}</td>
                <td>{{ order.user.username }}</td>
                <td>₹{{ order.total }}</td>
                <td>{{ order.status }}</td>
                <td>{{ order.created_at.strftime('%d %b %Y') }}</td>
                <td>
                    {% if order.status == 'Processing' %}
                    <form action="/admin/ship_order/{{ order.id }}" method="POST" style="display: inline;">
                        <button type="submit" class="btn-success">Mark Shipped</button>
                    </form>
                    {% elif order.status == 'Shipped' %}
                    <form action="/admin/deliver_order/{{ order.id }}" method="POST" style="display: inline;">
                        <button type="submit" class="btn-success">Mark Delivered</button>
                    </form>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <div style="background: white; padding: 40px; border-radius: 10px;">
        <h2>All Products</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Category</th>
                <th>Size</th>
                <th>Color</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Action</th>
            </tr>
            {% for product in products %}
            <tr>
                <td>{{ product.id }}</td>
                <td>{{ product.name }}</td>
                <td>{{ product.category }}</td>
                <td>{{ product.size }}</td>
                <td>{{ product.color }}</td>
                <td>₹{{ product.price }}</td>
                <td>{{ product.stock }}</td>
                <td>
                    <form action="/admin/delete_product/{{ product.id }}" method="POST">
                        <button type="submit" class="btn-danger" onclick="return confirm('Delete?')">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
""")

@app.route('/')
def home():
    products = Product.query.all()
    return render_template_string(HOME_PAGE, products=products)

@app.route('/products')
def products():
    category = request.args.get('category')
    if category:
        all_products = Product.query.filter_by(category=category).all()
    else:
        all_products = Product.query.all()
    return render_template_string(PRODUCTS_PAGE, products=all_products, category=category)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect('/register')
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created! Please login.', 'success')
        return redirect('/login')
    
    return render_template_string(REGISTER_PAGE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect('/')
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template_string(LOGIN_PAGE)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect('/')

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect('/login')
    
    product = Product.query.get_or_404(product_id)
    
    if product.stock <= 0:
        flash('Product out of stock!', 'error')
        return redirect('/products')
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    found = False
    
    for item in cart:
        if item['id'] == product_id:
            if item['quantity'] < product.stock:
                item['quantity'] += 1
                found = True
            else:
                flash('Not enough stock!', 'error')
                return redirect('/products')
            break
    
    if not found:
        cart.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'size': product.size,
            'color': product.color,
            'quantity': 1
        })
    
    session['cart'] = cart
    session.modified = True
    flash(f'{product.name} added to cart!', 'success')
    return redirect('/products')

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect('/login')
    
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    return render_template_string(CART_PAGE, cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        session['cart'] = [item for item in cart if item['id'] != product_id]
        session.modified = True
        flash('Item removed!', 'success')
    
    return redirect('/cart')

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return redirect('/login')
    
    cart_items = session.get('cart', [])
    address = request.form.get('address')
    
    if not cart_items:
        flash('Cart is empty!', 'error')
        return redirect('/cart')
    
    if not address:
        flash('Please provide shipping address!', 'error')
        return redirect('/cart')
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    # Update stock
    for item in cart_items:
        product = Product.query.get(item['id'])
        if product:
            product.stock -= item['quantity']
    
    # Create order
    new_order = Order(
        user_id=session['user_id'],
        total=total,
        items=json.dumps(cart_items),
        shipping_address=address,
        status='Processing'
    )
    db.session.add(new_order)
    db.session.commit()
    
    # Clear cart
    session['cart'] = []
    session.modified = True
    
    flash('Order placed successfully!', 'success')
    return redirect('/orders')

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    
    for order in user_orders:
        order.items_list = json.loads(order.items)
    
    return render_template_string(ORDERS_PAGE, orders=user_orders)

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        flash('Admin access required!', 'error')
        return redirect('/')
    
    all_products = Product.query.all()
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    
    return render_template_string(ADMIN_PAGE, products=all_products, orders=all_orders)

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if not session.get('is_admin'):
        return redirect('/')
    
    name = request.form['name']
    price = float(request.form['price'])
    description = request.form['description']
    category = request.form['category']
    size = request.form['size']
    color = request.form['color']
    stock = int(request.form['stock'])
    image = request.form['image']
    
    new_product = Product(
        name=name, price=price, description=description,
        category=category, size=size, color=color,
        stock=stock, image=image
    )
    db.session.add(new_product)
    db.session.commit()
    
    flash('Product added!', 'success')
    return redirect('/admin')

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('is_admin'):
        return redirect('/')
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted!', 'success')
    return redirect('/admin')

@app.route('/admin/ship_order/<int:order_id>', methods=['POST'])
def ship_order(order_id):
    if not session.get('is_admin'):
        return redirect('/')
    
    order = Order.query.get_or_404(order_id)
    order.status = 'Shipped'
    db.session.commit()
    
    flash('Order marked as shipped!', 'success')
    return redirect('/admin')

@app.route('/admin/deliver_order/<int:order_id>', methods=['POST'])
def deliver_order(order_id):
    if not session.get('is_admin'):
        return redirect('/')
    
    order = Order.query.get_or_404(order_id)
    order.status = 'Delivered'
    db.session.commit()
    
    flash('Order marked as delivered!', 'success')
    return redirect('/admin')


def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@fashion.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
        
        # Add sample clothing products
        if Product.query.count() == 0:
            clothing_items = [
                # Men's Collection
                Product(name='Classic White Shirt', price=1299, description='Premium cotton formal shirt', 
                       category='Men', size='L', color='White', stock=20,
                       image='https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400'),
                Product(name='Blue Denim Jeans', price=1899, description='Slim fit comfortable jeans',
                       category='Men', size='M', color='Blue', stock=15,
                       image='https://images.unsplash.com/photo-1542272604-787c3835535d?w=400'),
                Product(name='Black Leather Jacket', price=4999, description='Genuine leather biker jacket',
                       category='Men', size='XL', color='Black', stock=8,
                       image='https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400'),
                Product(name='Grey Hoodie', price=999, description='Comfortable cotton hoodie',
                       category='Men', size='L', color='Grey', stock=25,
                       image='https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400'),
                
                # Women's Collection
                Product(name='Floral Summer Dress', price=1599, description='Light and elegant summer dress',
                       category='Women', size='M', color='Floral', stock=18,
                       image='https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400'),
                Product(name='Black Evening Gown', price=3499, description='Elegant party wear gown',
                       category='Women', size='S', color='Black', stock=10,
                       image='https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=400'),
                Product(name='Casual Denim Jacket', price=1799, description='Trendy denim jacket',
                       category='Women', size='M', color='Blue', stock=12,
                       image='https://images.unsplash.com/photo-1601333144130-8cbb312386b6?w=400'),
                Product(name='White Top', price=799, description='Casual cotton top',
                       category='Women', size='S', color='White', stock=30,
                       image='https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=400'),
                
                # Kids Collection
                Product(name='Kids T-Shirt Set', price=699, description='Colorful printed t-shirts',
                       category='Kids', size='M', color='Multi', stock=25,
                       image='https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=400'),
                Product(name='Kids Denim Shorts', price=599, description='Comfortable summer shorts',
                       category='Kids', size='S', color='Blue', stock=20,
                       image='https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=400'),
                Product(name='Kids Party Dress', price=1299, description='Beautiful party wear dress',
                       category='Kids', size='L', color='Pink', stock=15,
                       image='https://images.unsplash.com/photo-1518831959646-742c3a14ebf7?w=400'),
                Product(name='Kids Winter Jacket', price=1499, description='Warm winter jacket',
                       category='Kids', size='M', color='Red', stock=12,
                       image='https://images.unsplash.com/photo-1514090458221-65bb69cf63e7?w=400'),
            ]
            
            for item in clothing_items:
                db.session.add(item)
        
        db.session.commit()
        print('✅ Fashion Store database initialized!')
        print('👤 Admin login: username=admin, password=admin123')


if _name_ == '_main_':
    init_db()
    print('\n' + '='*60)
    print('👔 Fashion Store is running!')
    print('📍 Open: http://127.0.0.1:5002')
    print('='*60 + '\n')
    app.run(debug=True, port=5002)