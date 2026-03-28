# E-commerce-Jewelry-Store

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask Version](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

Elegant & Timeless Beauty

A complete e-commerce jewelry store website built with Flask, featuring a fully functional admin panel, shopping cart, order management, and automated notification system (Email & SMS).

## ✨ Features

### 🛍️ Customer Features
- **Product Browsing** - Browse jewelry by categories (Necklaces, Earrings, Bangles, Rings, Anklets)
- **Product Details** - View detailed product information with images and descriptions
- **Shopping Cart** - Add/remove items, update quantities in real-time
- **Secure Checkout** - Multiple payment options (Cash on Delivery, bKash, Credit/Debit Card)
- **Order Confirmation** - Automatic email and SMS notifications
- **Responsive Design** - Fully optimized for mobile, tablet, and desktop devices

### 🔐 Admin Features
- **Secure Authentication** - Admin login system with session management
- **Dashboard Analytics** - View total products, orders, revenue, and low stock alerts
- **Product Management** - Add, edit, delete products with stock tracking
- **Order Management** - View orders, update status (Pending/Processing/Delivered), cancel orders
- **SMS Configuration** - Configure TextLocal API and SMS templates
- **Email Templates** - HTML email templates for order confirmation and status updates
- **Stock Alerts** - Automatic notifications for low stock items

### 📱 Notification System
- **Email Notifications** - Order confirmation and status updates via SMTP
- **SMS Notifications** - Order confirmation and status updates via TextLocal API
- **10 Pre-configured SMS Templates**:
  - Order Confirmation
  - Order Processing
  - Order Shipped
  - Order Delivered
  - Order Cancelled
  - Payment Reminder
  - Welcome SMS
  - Abandoned Cart
  - Festival Offer
  - Feedback Request

### 💾 Technical Features
- **No Database Required** - All data stored in JSON files
- **RESTful Architecture** - Clean URL routing
- **Session Management** - Secure user sessions
- **Bootstrap 5** - Modern, responsive UI framework
- **Font Awesome Icons** - Professional icon set
- **Mobile-First Design** - Optimized for all screen sizes

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/E-commerce-Jewelry-Store.git
cd E-commerce-Jewelry-Store

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

E-commerce-Jewelry-Store/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── products.json               # Product data (auto-generated)
├── orders.json                 # Order data (auto-generated)
├── sms_config.json            # SMS settings (auto-generated)
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css          # Custom styles
│   ├── js/
│   │   └── main.js            # JavaScript functionality
│   └── images/                 # Product images
│
├── templates/                  # HTML templates
│   ├── index.html             # Homepage
│   ├── products.html          # Product listing
│   ├── product_detail.html    # Product details
│   ├── cart.html              # Shopping cart
│   ├── checkout.html          # Checkout page
│   ├── about.html             # About us
│   ├── contact.html           # Contact page
│   │
│   └── admin/                 # Admin templates
│       ├── login.html         # Admin login
│       ├── dashboard.html     # Admin dashboard
│       ├── products.html      # Product management
│       ├── add_product.html   # Add product form
│       ├── edit_product.html  # Edit product form
│       ├── orders.html        # Order management
│       ├── view_order.html    # Order details
│       └── sms_settings.html  # SMS configuration
│
└── README.md                   # This file
