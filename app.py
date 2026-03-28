# app.py - Complete production-ready version with SMS templates
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
import os
import json
from functools import wraps
from flask_mail import Mail, Message
import requests
import re

app = Flask(__name__)
app.secret_key = 'shatsheeri_secret_key_2024_admin'

# Email Configuration (Update with your credentials)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_app_password'  # Replace with your app password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'shatsheeri2024'

# File paths
PRODUCTS_FILE = 'products.json'
ORDERS_FILE = 'orders.json'
SMS_CONFIG_FILE = 'sms_config.json'
SMS_TEMPLATES_FILE = 'sms_templates.json'

# SMS Templates
DEFAULT_SMS_TEMPLATES = {
    'order_confirmation': {
        'name': 'Order Confirmation',
        'template': 'Dear {customer_name}, Thank you for your order #{order_id} at Shatsheeri! Amount: ৳{total}. We will process it soon. Visit: shatsheeri.com',
        'variables': ['customer_name', 'order_id', 'total'],
        'active': True
    },
    'order_processing': {
        'name': 'Order Processing',
        'template': 'Dear {customer_name}, Your order #{order_id} at Shatsheeri is now being processed. We will ship it soon. Thank you for your patience!',
        'variables': ['customer_name', 'order_id'],
        'active': True
    },
    'order_shipped': {
        'name': 'Order Shipped',
        'template': 'Dear {customer_name}, Great news! Your order #{order_id} from Shatsheeri has been shipped. Expected delivery in 2-3 business days.',
        'variables': ['customer_name', 'order_id'],
        'active': True
    },
    'order_delivered': {
        'name': 'Order Delivered',
        'template': 'Dear {customer_name}, Your order #{order_id} from Shatsheeri has been delivered! Thank you for shopping with us. We hope you love your jewelry!',
        'variables': ['customer_name', 'order_id'],
        'active': True
    },
    'order_cancelled': {
        'name': 'Order Cancelled',
        'template': 'Dear {customer_name}, Your order #{order_id} at Shatsheeri has been cancelled. Amount ৳{total} will be refunded within 3-5 business days.',
        'variables': ['customer_name', 'order_id', 'total'],
        'active': True
    },
    'payment_reminder': {
        'name': 'Payment Reminder',
        'template': 'Dear {customer_name}, Reminder: Your order #{order_id} at Shatsheeri (৳{total}) is pending payment. Please complete payment within 24 hours.',
        'variables': ['customer_name', 'order_id', 'total'],
        'active': True
    },
    'welcome_sms': {
        'name': 'Welcome SMS',
        'template': 'Welcome to Shatsheeri, {customer_name}! Get 10% off on your first order. Use code: WELCOME10. Shop now: shatsheeri.com',
        'variables': ['customer_name'],
        'active': True
    },
    'abandoned_cart': {
        'name': 'Abandoned Cart',
        'template': 'Hi {customer_name}, You left items worth ৳{cart_total} in your cart at Shatsheeri! Complete your order now for express delivery.',
        'variables': ['customer_name', 'cart_total'],
        'active': True
    },
    'festival_offer': {
        'name': 'Festival Offer',
        'template': '🎉 Eid/Puja Special Offer! Up to 30% off on all jewelry at Shatsheeri. Limited time only! Shop now: shatsheeri.com/festival',
        'variables': [],
        'active': True
    },
    'feedback_request': {
        'name': 'Feedback Request',
        'template': 'Dear {customer_name}, How was your shopping experience at Shatsheeri? Please share your feedback: shatsheeri.com/review/{order_id}',
        'variables': ['customer_name', 'order_id'],
        'active': True
    }
}


def safe_json_load(filepath, default_data):
    """Safely load JSON data with error handling"""
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        return default_data

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                with open(filepath, 'w', encoding='utf-8') as f2:
                    json.dump(default_data, f2, indent=2, ensure_ascii=False)
                return default_data
            data = json.loads(content)

            # Validate and fix orders data structure
            if filepath == ORDERS_FILE and isinstance(data, list):
                for order in data:
                    if 'items' in order:
                        if not isinstance(order['items'], list):
                            order['items'] = []
                    else:
                        order['items'] = []

                    for i, item in enumerate(order['items']):
                        if not isinstance(item, dict):
                            order['items'][i] = {'name': 'Unknown', 'price': 0, 'quantity': 1}
                        else:
                            if 'name' not in item:
                                item['name'] = 'Unknown'
                            if 'price' not in item:
                                item['price'] = 0
                            if 'quantity' not in item:
                                item['quantity'] = 1

            return data
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error loading {filepath}: {e}")
        backup_file = f"{filepath}.backup"
        if os.path.exists(filepath):
            import shutil
            shutil.copy(filepath, backup_file)
            print(f"Backed up corrupted file to {backup_file}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        return default_data


def init_data_files():
    """Initialize all data files with default values"""
    # Default products data
    default_products = {
        'necklaces': [
            {'id': 1, 'name': 'Traditional Gold Necklace', 'price': 4500, 'image': '/static/images/necklace1.jpg',
             'category': 'Necklace',
             'description': 'Exquisite traditional gold-plated necklace with intricate design, perfect for weddings and festive occasions.',
             'stock': 10, 'featured': True},
            {'id': 2, 'name': 'Minimal Pearl Necklace', 'price': 2800, 'image': '/static/images/necklace2.jpg',
             'category': 'Necklace',
             'description': 'Elegant pearl necklace with minimal design, ideal for daily wear and office parties.',
             'stock': 15, 'featured': False},
            {'id': 3, 'name': 'Party Wear Choker', 'price': 3900, 'image': '/static/images/necklace3.jpg',
             'category': 'Necklace',
             'description': 'Stunning choker necklace with kundan work, perfect for parties and celebrations.',
             'stock': 8, 'featured': True}
        ],
        'earrings': [
            {'id': 4, 'name': 'Jhumka Earrings', 'price': 1200, 'image': '/static/images/earrings1.jpg',
             'category': 'Earrings',
             'description': 'Traditional jhumka earrings with delicate design, adds grace to any ethnic outfit.',
             'stock': 20, 'featured': False},
            {'id': 5, 'name': 'Stud Earrings Set', 'price': 800, 'image': '/static/images/earrings2.jpg',
             'category': 'Earrings', 'description': 'Modern stud earrings set in gold tone, comfortable for daily use.',
             'stock': 25, 'featured': True},
            {'id': 6, 'name': 'Hanging Chandelier', 'price': 2100, 'image': '/static/images/earrings3.jpg',
             'category': 'Earrings',
             'description': 'Elegant chandelier earrings with crystal work, perfect for evening parties.', 'stock': 12,
             'featured': False}
        ],
        'bangles': [
            {'id': 7, 'name': 'Gold Plated Bangle Set', 'price': 1800, 'image': '/static/images/bangles1.jpg',
             'category': 'Bangles',
             'description': 'Beautiful set of 4 gold-plated bangles with intricate carving, traditional charm.',
             'stock': 18, 'featured': True},
            {'id': 8, 'name': 'Kada Bracelet', 'price': 1500, 'image': '/static/images/bangles2.jpg',
             'category': 'Bangles',
             'description': 'Modern Kada bracelet with minimal design, suitable for both casual and formal wear.',
             'stock': 22, 'featured': False},
            {'id': 9, 'name': 'Stone Studded Bangle', 'price': 2200, 'image': '/static/images/bangles3.jpg',
             'category': 'Bangles',
             'description': 'Elegant stone-studded bangle with traditional motif, adds sparkle to your wrist.',
             'stock': 14, 'featured': False}
        ],
        'rings': [
            {'id': 10, 'name': 'Solitaire Ring', 'price': 3500, 'image': '/static/images/rings1.jpg',
             'category': 'Ring', 'description': 'Classic solitaire ring with cubic zirconia, timeless elegance.',
             'stock': 16, 'featured': True},
            {'id': 11, 'name': 'Adjustable Floral Ring', 'price': 600, 'image': '/static/images/rings2.jpg',
             'category': 'Ring', 'description': 'Adjustable ring with floral design, perfect for daily wear.',
             'stock': 30, 'featured': False},
            {'id': 12, 'name': 'Stackable Ring Set', 'price': 1800, 'image': '/static/images/rings3.jpg',
             'category': 'Ring', 'description': 'Set of 3 stackable rings with minimalist design, trendy and stylish.',
             'stock': 20, 'featured': False}
        ],
        'anklets': [
            {'id': 13, 'name': 'Silver Anklet', 'price': 900, 'image': '/static/images/anklets1.jpg',
             'category': 'Anklets',
             'description': 'Traditional silver-plated anklet with small bells, adds charm to your steps.', 'stock': 25,
             'featured': False},
            {'id': 14, 'name': 'Pearl Anklet Chain', 'price': 1100, 'image': '/static/images/anklets2.jpg',
             'category': 'Anklets', 'description': 'Elegant pearl anklet chain with adjustable length.', 'stock': 18,
             'featured': False},
            {'id': 15, 'name': 'Designer Anklet', 'price': 1600, 'image': '/static/images/anklets3.jpg',
             'category': 'Anklets', 'description': 'Designer anklet with intricate work and stone embellishments.',
             'stock': 12, 'featured': True}
        ]
    }

    default_orders = []
    default_sms_config = {
        'sms_enabled': False,
        'api_key': '',
        'sender_id': 'SHATSH',
        'default_template': 'order_confirmation'
    }

    safe_json_load(PRODUCTS_FILE, default_products)
    safe_json_load(ORDERS_FILE, default_orders)
    safe_json_load(SMS_CONFIG_FILE, default_sms_config)
    safe_json_load(SMS_TEMPLATES_FILE, DEFAULT_SMS_TEMPLATES)


def load_products():
    """Load products with error handling"""
    default_products = {
        'necklaces': [], 'earrings': [], 'bangles': [], 'rings': [], 'anklets': []
    }
    return safe_json_load(PRODUCTS_FILE, default_products)


def save_products(products):
    """Save products with error handling"""
    try:
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving products: {e}")
        return False


def load_orders():
    """Load orders with error handling"""
    return safe_json_load(ORDERS_FILE, [])


def save_orders(orders):
    """Save orders with error handling"""
    try:
        for order in orders:
            if 'items' not in order or not isinstance(order['items'], list):
                order['items'] = []
            order['items'] = [item for item in order['items'] if isinstance(item, dict)]

        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving orders: {e}")
        return False


def load_sms_config():
    """Load SMS config with error handling"""
    default_config = {'sms_enabled': False, 'api_key': '', 'sender_id': 'SHATSH',
                      'default_template': 'order_confirmation'}
    return safe_json_load(SMS_CONFIG_FILE, default_config)


def save_sms_config(config):
    """Save SMS config with error handling"""
    try:
        with open(SMS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving SMS config: {e}")
        return False


def load_sms_templates():
    """Load SMS templates with error handling"""
    return safe_json_load(SMS_TEMPLATES_FILE, DEFAULT_SMS_TEMPLATES)


def save_sms_templates(templates):
    """Save SMS templates with error handling"""
    try:
        with open(SMS_TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving SMS templates: {e}")
        return False


def format_phone_number(phone_number):
    """Format phone number for SMS gateway"""
    phone = re.sub(r'[^\d+]', '', phone_number.strip())
    if not phone.startswith('+') and not phone.startswith('88'):
        if phone.startswith('0'):
            phone = '+88' + phone[1:]
        else:
            phone = '+88' + phone
    return phone


def render_sms_template(template_key, variables):
    """Render SMS template with variables"""
    templates = load_sms_templates()
    template_data = templates.get(template_key, {})

    if not template_data or not template_data.get('active', False):
        # Fallback to default template
        template_data = DEFAULT_SMS_TEMPLATES.get('order_confirmation', {})

    template_text = template_data.get('template', '')

    # Replace variables
    for key, value in variables.items():
        template_text = template_text.replace(f'{{{key}}}', str(value))

    return template_text


def send_sms(phone_number, template_key, variables):
    """Send SMS using template"""
    try:
        sms_config = load_sms_config()
        if not sms_config.get('sms_enabled', False):
            print(f"SMS disabled. Would send {template_key} to: {phone_number}")
            return True

        phone = format_phone_number(phone_number)
        message = render_sms_template(template_key, variables)

        # Check message length
        if len(message) > 918:
            print(f"Message too long: {len(message)} characters. Truncating...")
            message = message[:915] + "..."

        api_key = sms_config.get('api_key', '')
        sender_id = sms_config.get('sender_id', 'SHATSH')

        if api_key and api_key != '':
            url = "https://api.textlocal.in/send/"
            data = {
                'apikey': api_key,
                'numbers': phone,
                'message': message,
                'sender': sender_id
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"SMS sent successfully to {phone}")
                    return True
                else:
                    print(f"SMS failed: {result}")
                    return False
            else:
                print(f"SMS HTTP error: {response.status_code}")
                return False
        else:
            print(f"[MOCK SMS] To: {phone} | Template: {template_key} | Message: {message}")
            return True

    except Exception as e:
        print(f"SMS sending failed: {e}")
        return False


def send_order_confirmation_sms(phone_number, order_id, customer_name, total):
    """Send order confirmation SMS using template"""
    return send_sms(phone_number, 'order_confirmation', {
        'customer_name': customer_name,
        'order_id': order_id,
        'total': total
    })


def send_order_status_sms(phone_number, customer_name, order_id, status):
    """Send order status SMS using appropriate template"""
    template_map = {
        'Processing': 'order_processing',
        'Shipped': 'order_shipped',
        'Delivered': 'order_delivered',
        'Cancelled': 'order_cancelled'
    }

    template_key = template_map.get(status, 'order_processing')

    variables = {
        'customer_name': customer_name,
        'order_id': order_id
    }

    # Add total for cancelled orders
    if status == 'Cancelled':
        # You would need to fetch the order total here
        variables['total'] = '0'  # This should be fetched from the order

    return send_sms(phone_number, template_key, variables)


def send_order_confirmation_email(customer_email, order_id, customer_name, order_items, total):
    """Send order confirmation email"""
    try:
        items_html = ""
        for item in order_items:
            items_html += f"""
              <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item.get('name', 'Unknown Product')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">{item.get('quantity', 1)}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">৳{item.get('price', 0)}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">৳{item.get('price', 0) * item.get('quantity', 1)}</td>
              </tr>
            """

        msg = Message(
            subject=f'Order Confirmation - Shatsheeri Order #{order_id}',
            recipients=[customer_email],
            html=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #C6A43F; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .order-details {{ margin: 20px 0; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th {{ background-color: #2C2C2C; color: white; padding: 10px; text-align: left; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                    .total {{ font-size: 18px; font-weight: bold; text-align: right; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>সাতঁসিড়ি – Shatsheeri</h1>
                        <p>Elegant & Timeless Beauty</p>
                    </div>
                    <div class="content">
                        <h2>Thank You for Your Order!</h2>
                        <p>Dear {customer_name},</p>
                        <p>We're pleased to confirm your order <strong>#{order_id}</strong>. We'll process it soon and keep you updated.</p>

                        <div class="order-details">
                            <h3>Order Details</h3>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Product</th>
                                        <th>Quantity</th>
                                        <th>Unit Price</th>
                                        <th>Subtotal</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items_html}
                                </tbody>
                            </table>
                            <div class="total">
                                <p>Total Amount: <strong>৳{total}</strong></p>
                            </div>
                        </div>

                        <p>We'll notify you when your order ships. If you have questions, contact us at info@shatsheeri.com</p>
                        <p>Thank you for choosing Shatsheeri!</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 সাতঁসিড়ি – Shatsheeri. All rights reserved.</p>
                        <p>Follow us on social media for updates and offers!</p>
                    </div>
                </div>
            </body>
            </html>
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_order_status_email(customer_email, customer_name, order_id, new_status):
    """Send order status update email"""
    try:
        status_messages = {
            'Processing': 'Your order is being processed and will be shipped soon.',
            'Shipped': 'Your order has been shipped and is on its way!',
            'Delivered': 'Your order has been delivered! Thank you for shopping with us.',
            'Cancelled': 'Your order has been cancelled. If you have any questions, please contact us.'
        }

        msg = Message(
            subject=f'Order Update - Shatsheeri Order #{order_id}',
            recipients=[customer_email],
            html=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #C6A43F; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .status {{ background-color: #C6A43F; color: white; padding: 10px; text-align: center; font-size: 18px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>সাতঁসিড়ি – Shatsheeri</h1>
                    </div>
                    <div class="content">
                        <h2>Order Status Update</h2>
                        <p>Dear {customer_name},</p>
                        <p>Your order <strong>#{order_id}</strong> status has been updated to:</p>
                        <div class="status">
                            <strong>{new_status}</strong>
                        </div>
                        <p>{status_messages.get(new_status, 'Thank you for your patience.')}</p>
                        <p>Track your order or contact us if you have any questions.</p>
                        <p>Thank you for choosing Shatsheeri!</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 সাতঁসিড়ি – Shatsheeri</p>
                    </div>
                </div>
            </body>
            </html>
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Status email failed: {e}")
        return False


# Admin login decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login to access admin panel', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return decorated_function


# Cart data structure
cart = {}


@app.route('/')
def home():
    products = load_products()
    featured_products = []
    for category in products:
        for product in products[category]:
            if product.get('featured', False):
                featured_products.append(product)
    return render_template('index.html', featured_products=featured_products[:6])


@app.route('/products/<category>')
def products_page(category):
    products = load_products()
    if category in products:
        product_list = products[category]
        return render_template('products.html', products=product_list, category=category.capitalize())
    return redirect(url_for('home'))


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    products = load_products()
    found_product = None
    for cat in products:
        for p in products[cat]:
            if p.get('id') == product_id:
                found_product = p
                break
        if found_product:
            break

    if found_product:
        return render_template('product_detail.html', product=found_product)
    return redirect(url_for('home'))


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    products = load_products()

    found_product = None
    for cat in products:
        for p in products[cat]:
            if p.get('id') == product_id:
                found_product = p
                break
        if found_product:
            break

    if found_product:
        if found_product.get('stock', 0) < quantity:
            flash(f'Sorry, only {found_product["stock"]} items available in stock!', 'danger')
            return redirect(request.referrer or url_for('home'))

        if product_id in cart:
            if cart[product_id]['quantity'] + quantity > found_product.get('stock', 0):
                flash(f'Cannot add {quantity} more. Only {found_product["stock"] - cart[product_id]["quantity"]} left!',
                      'danger')
                return redirect(request.referrer or url_for('home'))
            cart[product_id]['quantity'] += quantity
        else:
            cart[product_id] = {
                'id': found_product['id'],
                'name': found_product['name'],
                'price': found_product['price'],
                'quantity': quantity,
                'image': found_product.get('image', '/static/images/default.jpg')
            }
        flash(f'{found_product["name"]} added to cart!', 'success')

    return redirect(request.referrer or url_for('home'))


@app.route('/cart')
def view_cart():
    cart_items = list(cart.values())
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 0))
    products = load_products()

    found_product = None
    for cat in products:
        for p in products[cat]:
            if p.get('id') == product_id:
                found_product = p
                break
        if found_product:
            break

    if product_id in cart:
        if quantity > 0:
            if quantity > found_product.get('stock', 0):
                flash(f'Sorry, only {found_product["stock"]} items available!', 'danger')
                return redirect(url_for('view_cart'))
            cart[product_id]['quantity'] = quantity
        else:
            del cart[product_id]
    return redirect(url_for('view_cart'))


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if product_id in cart:
        del cart[product_id]
        flash('Item removed from cart!', 'info')
    return redirect(url_for('view_cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        payment_method = request.form.get('payment')

        cart_items = list(cart.values())
        total = sum(item['price'] * item['quantity'] for item in cart_items)

        orders = load_orders()
        new_order = {
            'id': len(orders) + 1,
            'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'customer': {
                'name': name,
                'email': email,
                'phone': phone,
                'address': address
            },
            'items': cart_items,
            'total': total,
            'payment_method': payment_method,
            'status': 'Pending',
            'order_status': 'Processing'
        }

        # Update stock
        products = load_products()
        for item in cart_items:
            for cat in products:
                for product in products[cat]:
                    if product.get('id') == item['id']:
                        product['stock'] = product.get('stock', 0) - item['quantity']
                        break

        save_products(products)
        orders.append(new_order)
        save_orders(orders)

        # Send notifications using templates
        email_sent = send_order_confirmation_email(email, new_order['id'], name, cart_items, total)
        sms_sent = send_order_confirmation_sms(phone, new_order['id'], name, total)

        notification_msg = "Order placed successfully! "
        if email_sent:
            notification_msg += "Confirmation email sent. "
        if sms_sent:
            notification_msg += "SMS confirmation sent."

        flash(notification_msg, 'success')
        cart.clear()
        return redirect(url_for('home'))

    cart_items = list(cart.values())
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('home'))
    return render_template('checkout.html', cart_items=cart_items, total=total)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


# Debug route
@app.route('/debug/orders')
@admin_required
def debug_orders():
    orders = load_orders()
    import pprint
    return f"<pre>Orders count: {len(orders)}\n\n{pprint.pformat(orders)}</pre>"


# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Welcome to Admin Panel!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'danger')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('home'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    products = load_products()
    orders = load_orders()

    total_products = sum(len(products[cat]) for cat in products)
    total_orders = len(orders)
    total_revenue = sum(order.get('total', 0) for order in orders if order.get('status') != 'Cancelled')
    low_stock_items = []

    for cat in products:
        for product in products[cat]:
            if product.get('stock', 0) <= 5:
                low_stock_items.append(product)

    return render_template('admin/dashboard.html',
                           total_products=total_products,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           low_stock_items=low_stock_items,
                           recent_orders=orders[-5:])


@app.route('/admin/products')
@admin_required
def admin_products():
    products = load_products()
    return render_template('admin/products.html', products=products)


@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = int(request.form.get('price'))
        category = request.form.get('category').lower()
        description = request.form.get('description')
        stock = int(request.form.get('stock'))
        featured = request.form.get('featured') == 'on'
        image = request.form.get('image', '/static/images/default.jpg')

        products = load_products()

        max_id = 0
        for cat in products:
            for product in products[cat]:
                if product.get('id', 0) > max_id:
                    max_id = product['id']

        new_product = {
            'id': max_id + 1,
            'name': name,
            'price': price,
            'image': image,
            'category': category.capitalize(),
            'description': description,
            'stock': stock,
            'featured': featured
        }

        if category not in products:
            products[category] = []

        products[category].append(new_product)
        save_products(products)

        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/add_product.html')


@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    products = load_products()
    found_product = None
    found_category = None

    for cat in products:
        for product in products[cat]:
            if product.get('id') == product_id:
                found_product = product
                found_category = cat
                break
        if found_product:
            break

    if not found_product:
        flash('Product not found!', 'danger')
        return redirect(url_for('admin_products'))

    if request.method == 'POST':
        found_product['name'] = request.form.get('name')
        found_product['price'] = int(request.form.get('price'))
        found_product['description'] = request.form.get('description')
        found_product['stock'] = int(request.form.get('stock'))
        found_product['featured'] = request.form.get('featured') == 'on'
        found_product['image'] = request.form.get('image', found_product.get('image', '/static/images/default.jpg'))

        new_category = request.form.get('category').lower()
        if new_category != found_category:
            products[found_category].remove(found_product)
            if new_category not in products:
                products[new_category] = []
            found_product['category'] = new_category.capitalize()
            products[new_category].append(found_product)

        save_products(products)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/edit_product.html', product=found_product, category=found_category)


@app.route('/admin/product/delete/<int:product_id>')
@admin_required
def admin_delete_product(product_id):
    products = load_products()
    deleted = False

    for cat in products:
        for product in products[cat]:
            if product.get('id') == product_id:
                products[cat].remove(product)
                deleted = True
                break
        if deleted:
            break

    if deleted:
        save_products(products)
        flash('Product deleted successfully!', 'success')
    else:
        flash('Product not found!', 'danger')

    return redirect(url_for('admin_products'))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = load_orders()
    return render_template('admin/orders.html', orders=orders)


@app.route('/admin/order/view/<int:order_id>')
@admin_required
def admin_view_order(order_id):
    orders = load_orders()
    order = None
    for o in orders:
        if o.get('id') == order_id:
            order = o
            break

    if not order:
        flash('Order not found!', 'danger')
        return redirect(url_for('admin_orders'))

    # SAFE: Ensure items is a list and not a method
    # Check if items exists and is a list
    if 'items' not in order:
        order['items'] = []
    elif not isinstance(order['items'], list):
        # If items is not a list (could be a method or something else), replace with empty list
        print(f"Warning: order.items is {type(order['items'])}, converting to list")
        order['items'] = []

    # Now safely iterate through items to clean them
    cleaned_items = []
    for item in order['items']:
        if isinstance(item, dict):
            cleaned_item = {
                'id': item.get('id', 0),
                'name': item.get('name', 'Unknown Product'),
                'price': item.get('price', 0),
                'quantity': item.get('quantity', 1),
                'image': item.get('image', '/static/images/default.jpg')
            }
            cleaned_items.append(cleaned_item)
        else:
            print(f"Warning: Found non-dict item: {item}")
            # Skip invalid items

    order['items'] = cleaned_items

    # Ensure customer info exists
    if 'customer' not in order or not isinstance(order['customer'], dict):
        order['customer'] = {
            'name': 'N/A',
            'email': 'N/A',
            'phone': 'N/A',
            'address': 'N/A'
        }

    return render_template('admin/view_order.html', order=order)

@app.route('/admin/order/update_status/<int:order_id>', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    status = request.form.get('status')
    orders = load_orders()

    for order in orders:
        if order.get('id') == order_id:
            old_status = order.get('status')
            order['status'] = status
            order['order_status'] = status

            if status != old_status and status != 'Pending':
                if order.get('customer'):
                    send_order_status_email(
                        order['customer'].get('email', ''),
                        order['customer'].get('name', 'Customer'),
                        order_id,
                        status
                    )
                    send_order_status_sms(
                        order['customer'].get('phone', ''),
                        order['customer'].get('name', 'Customer'),
                        order_id,
                        status
                    )

            flash(f'Order #{order_id} status updated to {status}!', 'success')
            break

    save_orders(orders)
    return redirect(url_for('admin_orders'))


@app.route('/admin/order/cancel/<int:order_id>')
@admin_required
def admin_cancel_order(order_id):
    orders = load_orders()
    products = load_products()

    for order in orders:
        if order.get('id') == order_id:
            if order.get('status') != 'Cancelled':
                for item in order.get('items', []):
                    if isinstance(item, dict):
                        for cat in products:
                            for product in products[cat]:
                                if product.get('id') == item.get('id'):
                                    product['stock'] = product.get('stock', 0) + item.get('quantity', 0)
                                    break

                order['status'] = 'Cancelled'
                order['order_status'] = 'Cancelled'
                save_products(products)
                save_orders(orders)

                if order.get('customer'):
                    send_order_status_email(
                        order['customer'].get('email', ''),
                        order['customer'].get('name', 'Customer'),
                        order_id,
                        'Cancelled'
                    )
                    send_order_status_sms(
                        order['customer'].get('phone', ''),
                        order['customer'].get('name', 'Customer'),
                        order_id,
                        'Cancelled'
                    )

                flash(f'Order #{order_id} has been cancelled and stock restored! Notifications sent.', 'success')
            else:
                flash('Order is already cancelled!', 'warning')
            break

    return redirect(url_for('admin_orders'))


@app.route('/admin/sms_settings', methods=['GET', 'POST'])
@admin_required
def admin_sms_settings():
    if request.method == 'POST':
        config = {
            'sms_enabled': request.form.get('sms_enabled') == 'on',
            'api_key': request.form.get('api_key'),
            'sender_id': request.form.get('sender_id', 'SHATSH'),
            'default_template': request.form.get('default_template', 'order_confirmation')
        }
        save_sms_config(config)
        flash('SMS settings saved successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    config = load_sms_config()
    templates = load_sms_templates()
    return render_template('admin/sms_settings.html', config=config, templates=templates)


@app.route('/admin/sms_templates', methods=['GET', 'POST'])
@admin_required
def admin_sms_templates():
    if request.method == 'POST':
        templates = load_sms_templates()
        template_key = request.form.get('template_key')

        if template_key in templates:
            templates[template_key]['template'] = request.form.get('template')
            templates[template_key]['active'] = request.form.get('active') == 'on'
            save_sms_templates(templates)
            flash(f'Template "{templates[template_key]["name"]}" updated successfully!', 'success')

        return redirect(url_for('admin_sms_templates'))

    templates = load_sms_templates()
    return render_template('admin/sms_templates.html', templates=templates)


@app.route('/admin/test_sms', methods=['POST'])
@admin_required
def test_sms():
    data = request.get_json()
    phone = data.get('phone')
    template_key = data.get('template', 'order_confirmation')

    if not phone:
        return jsonify({'success': False, 'message': 'Phone number required'})

    success = send_sms(phone, template_key, {
        'customer_name': 'Test Customer',
        'order_id': 'TEST123',
        'total': '1500',
        'cart_total': '2500'
    })

    if success:
        return jsonify({'success': True, 'message': 'Test SMS sent successfully!'})
    else:
        return jsonify({'success': False, 'message': 'SMS configuration may be incorrect'})


if __name__ == '__main__':
    init_data_files()
    app.run(debug=True)