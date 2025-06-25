from flask import Flask, jsonify, render_template, request, session
from flask_mysqldb import MySQL
from collections import defaultdict
import calendar
from datetime import datetime, timedelta
from flask import send_from_directory
from routes.routes import routes
import bcrypt
from flask_cors import CORS
from MySQLdb.cursors import DictCursor
from fpdf import FPDF
import os
import stripe
import uuid

# Import DSS module
from dss import init_dss_routes


app = Flask(__name__, template_folder='.')

app.secret_key = 'my_super_secure_key_123'
app.permanent_session_lifetime = timedelta(days=1)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  

CORS(app, supports_credentials=True)

# Stripe configuration
stripe.api_key = 'sk_test_51JY6DwHmNGByIcZOsJbjlzGX4Hx2OHOm9jjDcfLAG5utDgtmh1mLRDymt8zvrFR15Ha8CPLNRTF2q5okGbr7O7rd00N4l6zrfg'  

# flask_mysqldb with XAMPP
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'dogarmedicalstore'
app.config['MYSQL_HOST'] = 'localhost'

mysql = MySQL(app)

# Register main routes
app.register_blueprint(routes)

# Initialize and register DSS routes properly
init_dss_routes(app, mysql)


@app.route("/signsup", methods=["POST"])
def signsup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    role = data.get("role")  

    print("📥 Received Signup Data:", data)

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO users (username, first_name, last_name, email, password, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, first_name, last_name, email, hashed_pw, role))
        mysql.connection.commit()
        cur.close()
        print("✅ Signup saved successfully.")
        return "Signup successful", 200
    except Exception as e:
        print("❌ Signup Error:", str(e))
        return f"An error occurred: {str(e)}", 400


@app.route("/signsin", methods=["POST"])
def signsin():
    data = request.get_json()
    email = data.get("email").strip()
    password = data.get("password").strip()

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            stored_password = user[5]
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                session.permanent = True
                session['role'] = user[6]
                session['user_id'] = user[0]

                print("✅ SESSION SET:", session)

                return jsonify({
                    "success": True,
                    "message": "Login successful!",
                    "role": user[6]
                })
            else:
                return jsonify({"success": False, "message": "Incorrect password!"})
        else:
            return jsonify({"success": False, "message": "Email not found!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/whoami")
def whoami():
    return jsonify({
        "role": session.get("role"),
        "user_id": session.get("user_id")
    })


@app.route('/')
def home():
    return render_template('home.html')


# Customer Profile APIs
@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        
        if user:
            user_data = {
                'id': user[0],
                'username': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'email': user[4],
                'role': user[6],
                'phone': user[7] if len(user) > 7 else None,
                'date_of_birth': user[8] if len(user) > 8 else None,
                'address': user[9] if len(user) > 9 else None,
                'city': user[10] if len(user) > 10 else None,
                'postal_code': user[11] if len(user) > 11 else None
            }
            return jsonify(user_data)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/update-profile', methods=['PUT'])
def update_profile():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"success": False, "message": "Not authenticated"}), 401
        
        data = request.get_json()
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE users SET 
                first_name = %s, 
                last_name = %s, 
                phone = %s, 
                date_of_birth = %s, 
                address = %s, 
                city = %s, 
                postal_code = %s
            WHERE id = %s
        """, (
            data.get('first_name'),
            data.get('last_name'),
            data.get('phone'),
            data.get('date_of_birth'),
            data.get('address'),
            data.get('city'),
            data.get('postal_code'),
            user_id
        ))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"success": True, "message": "Profile updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/change-password', methods=['PUT'])
def change_password():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"success": False, "message": "Not authenticated"}), 401
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        
        if user and bcrypt.checkpw(current_password.encode('utf-8'), user[0].encode('utf-8')):
            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_new_password, user_id))
            mysql.connection.commit()
            cur.close()
            return jsonify({"success": True, "message": "Password changed successfully"})
        else:
            cur.close()
            return jsonify({"success": False, "message": "Current password is incorrect"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/my-orders', methods=['GET'])
def get_my_orders():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify([])
        
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT o.order_id, o.order_date, o.total_amount, COUNT(oi.order_item_id) as item_count
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.customer_id = %s
            GROUP BY o.order_id
            ORDER BY o.order_date DESC
            LIMIT 10
        """, (user_id,))
        
        orders = []
        for row in cur.fetchall():
            orders.append({
                'order_id': row[0],
                'order_date': row[1],
                'total_amount': row[2],
                'item_count': row[3]
            })
        
        cur.close()
        return jsonify(orders)
    except Exception as e:
        return jsonify([])


# Admin User Management APIs
@app.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, first_name, last_name, email, role FROM users ORDER BY id DESC")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        cur.close()
        
        users = [dict(zip(column_names, row)) for row in rows]
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/users', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        
        # Hash password
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO users (username, first_name, last_name, email, password, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['username'],
            data['firstName'],
            data['lastName'],
            data['email'],
            hashed_password,
            data['role']
        ))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"success": True, "message": "User added successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        
        cur = mysql.connection.cursor()
        
        # Build update query
        if 'password' in data and data['password']:
            # Update with password
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute("""
                UPDATE users SET 
                    username = %s, 
                    first_name = %s, 
                    last_name = %s, 
                    email = %s, 
                    password = %s, 
                    role = %s
                WHERE id = %s
            """, (
                data['username'],
                data['firstName'],
                data['lastName'],
                data['email'],
                hashed_password,
                data['role'],
                user_id
            ))
        else:
            # Update without password
            cur.execute("""
                UPDATE users SET 
                    username = %s, 
                    first_name = %s, 
                    last_name = %s, 
                    email = %s, 
                    role = %s
                WHERE id = %s
            """, (
                data['username'],
                data['firstName'],
                data['lastName'],
                data['email'],
                data['role'],
                user_id
            ))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"success": True, "message": "User updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"success": True, "message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# Customer Ledger API
@app.route('/api/customer-ledger/<int:customer_id>', methods=['GET'])
def get_customer_ledger(customer_id):
    try:
        cur = mysql.connection.cursor()
        
        # Get customer info
        cur.execute("SELECT id, username, first_name, last_name, email FROM users WHERE id = %s", (customer_id,))
        customer_info = cur.fetchone()
        
        if not customer_info:
            return jsonify({"error": "Customer not found"}), 404
        
        customer_data = {
            'id': customer_info[0],
            'name': f"{customer_info[2]} {customer_info[3]}",
            'email': customer_info[4]
        }
        
        # Get all transactions for this customer
        cur.execute("""
            SELECT 
                o.order_date as date,
                o.order_id as inv_no,
                'Med-Sales' as trans_type,
                oi.product_name as item_name,
                CONCAT(oi.product_name, ' - Qty: ', oi.quantity) as description,
                oi.quantity as qty,
                oi.unit_price as rate,
                0 as credit_amount,
                oi.total_price as debit_amount,
                'Dr' as dr_cr
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.customer_id = %s
            
            UNION ALL
            
            SELECT 
                o.order_date as date,
                o.order_id as inv_no,
                'Receipt Vouc' as trans_type,
                'Cash Payment' as item_name,
                CONCAT('Payment for Order #', o.order_id) as description,
                1 as qty,
                o.paid_amount as rate,
                o.paid_amount as credit_amount,
                0 as debit_amount,
                'Cr' as dr_cr
            FROM orders o
            WHERE o.customer_id = %s AND o.paid_amount > 0
            
            ORDER BY date ASC, inv_no ASC
        """, (customer_id, customer_id))
        
        transactions = []
        running_balance = 0.0
        
        for row in cur.fetchall():
            debit_amount = float(row[8]) if row[8] else 0.0
            credit_amount = float(row[7]) if row[7] else 0.0
            
            # Calculate running balance (Debit increases balance, Credit decreases)
            running_balance += debit_amount - credit_amount
            
            transaction = {
                'date': row[0],
                'inv_no': row[1],
                'trans_type': row[2],
                'item_name': row[3],
                'description': row[4],
                'qty': row[5],
                'rate': float(row[6]) if row[6] else 0.0,
                'credit_amount': credit_amount,
                'debit_amount': debit_amount,
                'balance': running_balance,
                'dr_cr': 'Dr' if running_balance >= 0 else 'Cr'
            }
            transactions.append(transaction)
        
        # Calculate summary
        total_debit = sum(t['debit_amount'] for t in transactions)
        total_credit = sum(t['credit_amount'] for t in transactions)
        
        summary = {
            'opening_balance': 0.0,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'ending_balance': running_balance
        }
        
        cur.close()
        
        return jsonify({
            'customer_info': customer_data,
            'transactions': transactions,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#inventory
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT product_id, product_name, brand, price, 
                stock_quantity, category, expiry_date, image_path
            FROM products
            WHERE stock_quantity > 0
            ORDER BY product_name

        """)
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        cur.close()

        
        products = [dict(zip(column_names, row)) for row in rows]

        return jsonify(products)
    except Exception as err:
        return jsonify({"error": f"MySQL Error: {str(err)}"}), 500


# Add new product
@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.form
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Save image to pictures folder
                image_filename = f"product_{data['product_id']}_{image.filename}"
                image_path = f"/pictures/{image_filename}"
                image.save(f"pictures/{image_filename}")
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO products (product_id, product_name, brand, description, price, 
                                stock_quantity, category, expiry_date, image_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['product_id'],
            data['product_name'],
            data.get('brand', 'Generic'),
            data.get('description', ''),
            float(data['price']),
            int(data['stock_quantity']),
            data['category'],
            data['expiry_date'] if data['expiry_date'] else None,
            image_path
        ))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"message": "Product added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Update product
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.form
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                image_filename = f"product_{product_id}_{image.filename}"
                image_path = f"/pictures/{image_filename}"
                image.save(f"pictures/{image_filename}")
        
        cur = mysql.connection.cursor()
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        if 'product_name' in data:
            update_fields.append("product_name = %s")
            values.append(data['product_name'])
        
        if 'brand' in data:
            update_fields.append("brand = %s")
            values.append(data.get('brand', 'Generic'))
        
        if 'description' in data:
            update_fields.append("description = %s")
            values.append(data.get('description', ''))
        
        if 'price' in data:
            update_fields.append("price = %s")
            values.append(float(data['price']))
        
        if 'stock_quantity' in data:
            update_fields.append("stock_quantity = %s")
            values.append(int(data['stock_quantity']))
        
        if 'category' in data:
            update_fields.append("category = %s")
            values.append(data['category'])
        
        if 'expiry_date' in data and data['expiry_date']:
            update_fields.append("expiry_date = %s")
            values.append(data['expiry_date'])
        
        if image_path:
            update_fields.append("image_path = %s")
            values.append(image_path)
        
        if update_fields:
            query = f"UPDATE products SET {', '.join(update_fields)} WHERE product_id = %s"
            values.append(product_id)
            cur.execute(query, values)
            mysql.connection.commit()
        
        cur.close()
        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Delete product
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Customer API endpoints
@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, first_name, last_name, email, role FROM users")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        cur.close()
        
        customers = [dict(zip(column_names, row)) for row in rows]
        return jsonify(customers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/customer-orders', methods=['GET'])
def get_customer_orders():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT order_id, customer_id, total_amount, order_date, payment_status FROM orders WHERE customer_id IS NOT NULL")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        cur.close()
        
        orders = [dict(zip(column_names, row)) for row in rows]
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/customer-order-details/<int:customer_id>', methods=['GET'])
def get_customer_order_details(customer_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT o.order_id, o.total_amount, o.order_date,
               oi.product_name, oi.quantity, oi.unit_price, o.payment_status
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.customer_id = %s
            ORDER BY o.order_date DESC
        """, (customer_id,))
        
        rows = cur.fetchall()
        cur.close()
        
        # Group items by order
        orders = {}
        for row in rows:
            order_id = row[0]
            if order_id not in orders:
                orders[order_id] = {
                    'order_id': order_id,
                    'total_amount': row[1],
                    'order_date': row[2],
                    'payment_status': row[6],  
                    'items': []
                }
            
            if row[3]:  # If there are items
                orders[order_id]['items'].append({
                    'product_name': row[3],
                    'quantity': row[4],
                    'unit_price': row[5]
                })
        
        return jsonify(list(orders.values()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#invetory order for pharmacy


@app.route('/save_pharmacy_order', methods=['POST'])
def save_pharmacy_order():
    data = request.json
    supplier_name = data.get('supplier_name')
    expected_delivery_date = data.get('expected_delivery_date')
    items = data.get('items')

    if not supplier_name or not expected_delivery_date or not items:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        total_amount = sum(item['quantity'] * item['price'] for item in items)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO pharmacy_orders (supplier_name, expected_delivery_date, total_amount)
            VALUES (%s, %s, %s)
        """, (supplier_name, expected_delivery_date, total_amount))
        pharmacy_order_id = cur.lastrowid

        for item in items:
            cur.execute("""
                INSERT INTO pharmacy_order_items (pharmacy_order_id, product_name, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
            """, (
                pharmacy_order_id,
                item['name'],
                item['quantity'],
                item['price']
            ))

        mysql.connection.commit()
        cur.close()

        # Generate formatted PDF
        pdf_path = generate_pharmacy_order_pdf(
            order_id=pharmacy_order_id,
            supplier_name=supplier_name,
            expected_delivery_date=expected_delivery_date,
            items=items,
            total_amount=total_amount
        )

        return jsonify({
            "message": "Order saved successfully",
            "pdf_url": f"/download_order_pdf/{os.path.basename(pdf_path)}"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download_order_pdf/<filename>')
def download_order_pdf(filename):
    try:
        return send_from_directory('orders', filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404



def generate_pharmacy_order_pdf(order_id, supplier_name, expected_delivery_date, items, total_amount):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Heading
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "Dogar Pharmacy", ln=True, align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 14)
    pdf.ln(5)
    pdf.cell(0, 10, f"Purchase Order #: PO-{order_id}", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Expected Delivery: {expected_delivery_date}", ln=True)
    pdf.cell(0, 10, f"Order Date: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", ln=True)
    pdf.ln(10)

    # Table Headers
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(240, 240, 255)
    pdf.cell(80, 10, "Product", 1, 0, "C", True)
    pdf.cell(30, 10, "Quantity", 1, 0, "C", True)
    pdf.cell(30, 10, "Unit Price", 1, 0, "C", True)
    pdf.cell(40, 10, "Total", 1, 1, "C", True)

    # Table Data
    pdf.set_font("Arial", "", 12)
    for item in items:
        total = item['quantity'] * item['price']
        pdf.cell(80, 10, item['name'], 1)
        pdf.cell(30, 10, str(item['quantity']), 1, 0, "C")
        pdf.cell(30, 10, f"Rs. {item['price']}", 1, 0, "C")
        pdf.cell(40, 10, f"Rs. {total}", 1, 1, "C")

    # Total
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, "Total Amount", 1)
    pdf.cell(40, 10, f"Rs. {total_amount:.2f}", 1, 1, "C")

    # Save PDF
    pdf_folder = "orders"
    os.makedirs(pdf_folder, exist_ok=True)
    filename = f"order_{order_id}.pdf"
    path = os.path.join(pdf_folder, filename)
    pdf.output(path)

    return path


# Stripe Payment Intent Creation
@app.route('/api/create_payment_intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.json
        amount = data.get('amount')  # Amount in cents
        currency = data.get('currency', 'pkr')
        cart = data.get('cart', [])

        # Create payment intent with Stripe
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={
                'cart_items': str(len(cart)),
                'user_id': str(session.get('user_id', 'guest'))
            }
        )

        return jsonify({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Save Customer Order with Payment Details
@app.route('/api/save_customer_order', methods=['POST'])
def save_customer_order():
    data = request.json
    cart = data.get('cart', [])
    total_amount = data.get('total_amount', 0)
    paid_amount = data.get('paid_amount', 0)
    change_amount = data.get('change_amount', 0)
    payment_method = data.get('payment_method', 'stripe')
    payment_intent_id = data.get('payment_intent_id')
    card_holder = data.get('card_holder')
    card_last_four = data.get('card_last_four')

    if not cart:
        return jsonify({"error": "Cart is empty."}), 400

    try:
        cur = mysql.connection.cursor()
        
        # Insert order with payment details
        cur.execute("""
            INSERT INTO orders (customer_id, order_date, total_amount, paid_amount, change_amount, 
                              payment_method, payment_intent_id, card_holder, card_last_four)
            VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, %s)
        """, (session.get('user_id'), total_amount, paid_amount, change_amount, 
              payment_method, payment_intent_id, card_holder, card_last_four))
        
        order_id = cur.lastrowid

        # Insert order items and update stock
        for item in cart:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                order_id,
                item['product_id'],
                item['name'],
                item['quantity'],
                item['price'],
                item['price'] * item['quantity']
            ))
            
            # Update product stock
            cur.execute("""
                UPDATE products 
                SET stock_quantity = stock_quantity - %s 
                WHERE product_id = %s AND stock_quantity >= %s
            """, (item['quantity'], item['product_id'], item['quantity']))
            
            # Check if stock update was successful
            if cur.rowcount == 0:
                mysql.connection.rollback()
                cur.close()
                return jsonify({"error": f"Insufficient stock for {item['name']}"}), 400

        mysql.connection.commit()

        # Generate customer receipt PDF
        pdf_path = generate_customer_receipt_pdf(
            order_id=order_id,
            cart=cart,
            total_amount=total_amount,
            paid_amount=paid_amount,
            change_amount=change_amount,
            card_holder=card_holder,
            card_last_four=card_last_four
        )

        cur.close()

        return jsonify({
            "success": True,
            "order_id": order_id,
            "pdf_url": f"/download_customer_receipt/{os.path.basename(pdf_path)}"
        })

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500


def generate_customer_receipt_pdf(order_id, cart, total_amount, paid_amount, change_amount, card_holder, card_last_four):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Pharmacy Header
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(19, 139, 168)
    pdf.cell(0, 12, "PHARMA MASTERMIND", ln=True, align="C")

    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, "Dogar Pharmacy", ln=True, align="C")
    pdf.cell(0, 6, "Bucha Chatta", ln=True, align="C")
    pdf.cell(0, 6, "License Number: 3088-6987456", ln=True, align="C")
    pdf.cell(0, 6, "Tel: 0321-1234567", ln=True, align="C")
    pdf.ln(5)
    
    # Separator line
    pdf.set_draw_color(19, 139, 168)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)

    # Receipt Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"CUSTOMER RECEIPT", ln=True, align="C")
    pdf.ln(3)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 6, f"Receipt No: CR-{order_id}", border=0)
    pdf.cell(95, 6, datetime.now().strftime("%d %b %Y   %H:%M"), ln=True, align="R")
    pdf.cell(95, 6, f"Customer: {card_holder}", border=0)
    pdf.cell(95, 6, f"Card: ****{card_last_four}", ln=True, align="R")
    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 248, 255)
    pdf.cell(25, 8, "Qty", border=1, align="C", fill=True)
    pdf.cell(105, 8, "Product Description", border=1, align="C", fill=True)
    pdf.cell(30, 8, "Unit Price", border=1, align="C", fill=True)
    pdf.cell(30, 8, "Total", border=1, align="C", fill=True)
    pdf.ln()

    # Table Items
    pdf.set_font("Arial", "", 9)
    for item in cart:
        item_total = item['price'] * item['quantity']
        pdf.cell(25, 7, str(item['quantity']), border=1, align="C")
        pdf.cell(105, 7, item['name'][:45], border=1)  # Truncate long names
        pdf.cell(30, 7, f"Rs. {item['price']:.2f}", border=1, align="R")
        pdf.cell(30, 7, f"Rs. {item_total:.2f}", border=1, align="R")
        pdf.ln()

    # Summary Section
    pdf.ln(5)
    pdf.set_font("Arial", "", 10)
    
    # Summary box
    summary_y = pdf.get_y()
    pdf.rect(130, summary_y, 60, 35)
    
    pdf.set_xy(135, summary_y + 3)
    pdf.cell(50, 6, f"Subtotal: Rs. {total_amount:.2f}", ln=True)
    pdf.set_x(135)
    pdf.cell(50, 6, f"Tax: Rs. 0.00", ln=True)
    pdf.set_x(135)
    pdf.cell(50, 6, f"Discount: Rs. 0.00", ln=True)
    pdf.set_x(135)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 6, f"Total: Rs. {total_amount:.2f}", ln=True)
    pdf.set_x(135)
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, f"Paid: Rs. {paid_amount:.2f}", ln=True)

    # Payment method info
    pdf.ln(8)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"Payment Method: Credit/Debit Card (****{card_last_four})", ln=True, align="C")
    pdf.cell(0, 6, "Payment Status: APPROVED", ln=True, align="C")

    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Thank You for Shopping with Us!", ln=True, align="C")
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 5, "For any queries, please contact us at support@pharmamaster.com", ln=True, align="C")
    pdf.cell(0, 5, "Visit us online: www.pharmamaster.com", ln=True, align="C")

    # Save PDF
    pdf_folder = "customer_receipts"
    os.makedirs(pdf_folder, exist_ok=True)
    filename = f"customer_receipt_{order_id}.pdf"
    path = os.path.join(pdf_folder, filename)
    pdf.output(path)

    return path


@app.route('/download_customer_receipt/<filename>')
def download_customer_receipt(filename):
    try:
        return send_from_directory('customer_receipts', filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


#POS


@app.route('/api/save_order', methods=['POST'])
def save_order():
    data = request.json
    cart = data.get('cart', [])
    paid_amount = data.get('paid_amount', 0)
    change_amount = data.get('change_amount', 0)

    if not cart:
        return jsonify({"error": "Cart is empty."}), 400

    try:
        total_amount = sum(item['price'] * item['quantity'] for item in cart)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO orders (order_date, total_amount, paid_amount, change_amount)
            VALUES (NOW(), %s, %s, %s)
        """, (total_amount, paid_amount, change_amount))
        order_id = cur.lastrowid

        for item in cart:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                order_id,
                item['product_id'],
                item['name'],
                item['quantity'],
                item['price'],
                item['price'] * item['quantity']
            ))

        mysql.connection.commit()
        cur.close()

        # === Generate PDF Receipt ===
        os.makedirs("receipts", exist_ok=True)
        pdf = FPDF()
        pdf.add_page()

        # Pharmacy Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "DOGAR PHARMACY", ln=True, align="C")

        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 8, "Bucha Chatta", ln=True, align="C")
        pdf.cell(190, 8, "License Number: 3088-6987456", ln=True, align="C")
        pdf.cell(190, 8, "Tel: 0321-1234567", ln=True, align="C")
        pdf.ln(3)
        pdf.cell(190, 0, "", ln=True, border="T")
        pdf.ln(4)

        # Invoice Info
        pdf.set_font("Arial", "", 11)
        pdf.cell(95, 8, f"Invoice No: TI{order_id}", border=0)
        pdf.cell(95, 8, datetime.now().strftime("%d %b %Y   %H:%M"), ln=True, align="R")
        pdf.ln(4)

        # Table Header
        pdf.set_font("Arial", "B", 11)
        pdf.cell(30, 8, "Qty", border=1, align="C")
        pdf.cell(100, 8, "Description", border=1, align="C")
        pdf.cell(60, 8, "Price", border=1, align="C")
        pdf.ln()

        # Table Items
        pdf.set_font("Arial", "", 11)
        for item in cart:
            quantity = str(item['quantity'])
            name = item['name']
            price = f"{item['price'] * item['quantity']:.2f}"
            pdf.cell(30, 8, quantity, border=1, align="C")
            pdf.cell(100, 8, name, border=1)
            pdf.cell(60, 8, price, border=1, align="R")
            pdf.ln()

        # Summary
        pdf.ln(4)
        pdf.set_font("Arial", "", 11)
        pdf.cell(190, 8, f"Total: {total_amount:.2f}", ln=True, align="R")
        pdf.cell(190, 8, f"Tax Included: 0.0", ln=True, align="R")
        pdf.cell(190, 8, f"Discount: 0.0", ln=True, align="R")
        pdf.cell(190, 8, f"Paid Amount: {paid_amount:.2f}", ln=True, align="R")
        pdf.cell(190, 8, f"Change: {change_amount:.2f}", ln=True, align="R")

        # Thank You Note
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "Thank You!", ln=True, align="C")

        # Save PDF
        pdf_filename = f"receipt_{order_id}.pdf"
        pdf_path = os.path.join("receipts", pdf_filename)
        pdf.output(pdf_path)

        return jsonify({
            "success": True,
            "order_id": order_id,
            "pdf_url": f"/download_receipt/{pdf_filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_receipt/<filename>')
def download_receipt(filename):
    try:
        return send_from_directory('receipts', filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# Invoice Generation
from MySQLdb.cursors import DictCursor

@app.route('/api/invoice/<order_id>')
def get_invoice(order_id):
    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    # Fetch order
    cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    order = cursor.fetchone()

    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Fetch order items
    cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
    items = cursor.fetchall()

    return jsonify({
        "order": order,
        "items": items
    }), 200


# Get all employees

@app.route('/employees/add', methods=['POST'])
def add_employee():
    data = request.get_json()
    try:
        print("Received data:", data)  # Debug print
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO employees 
            (employee_id, name, email, phone, cnic, emergency, role, salary) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['id'], data['name'], data['email'], data['phone'],
            data['cnic'], data['emergency_contact'],  # 🛠 Fix: mapping this correctly
            data['role'], data['salary']
        ))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/employees', methods=['GET'])
def get_employees():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM employees')
        rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]
        employees = [dict(zip(col_names, row)) for row in rows]
        cur.close()
        return jsonify(employees)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Update employee
@app.route('/api/employees/<string:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    try:
        data = request.json
        cur = mysql.connection.cursor()
        query = '''
            UPDATE employees
            SET name=%s, email=%s, phone=%s, cnic=%s,
                emergency=%s, role=%s, salary=%s
            WHERE employee_id=%s
        '''
        values = (
            data['name'], data['email'], data['phone'], data['cnic'],
            data['emergency_contact'], data['role'], data['salary'], emp_id
        )
        cur.execute(query, values)
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Employee updated successfully'})
    except Exception as e:
        print("Update error:", e)
        return jsonify({'error': str(e)}), 500



# Delete employee
@app.route('/api/employees/<string:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM employees WHERE employee_id = %s", (emp_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Employee deleted successfully'})
    except Exception as e:
        print("Delete error:", e)
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)