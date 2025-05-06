# import appropriate libraries
from flask import Flask,flash, session, render_template, request, redirect, url_for, send_from_directory, jsonify, make_response
import os
import io
from io import BytesIO
from datetime import datetime, timedelta
import re
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
import psycopg2
from psycopg2 import sql, errors
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash # password hashing
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Direct flask to templates folder
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create invoice folder to store downloaded invoices
app.config['UPLOAD_FOLDER'] = 'invoices'
# Create receipts folder to store downloaded receipts
app.config['RECEIPT_FOLDER'] = 'receipts'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size


# Database configuration
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )


# Current date function
def get_current_date():
    return datetime.now().strftime('%Y-%m-%d')


# Current time function
def get_current_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# Create the next invoice number
def get_next_invoice_number():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        current_month = datetime.now().strftime('%m') # Month
        current_year = datetime.now().strftime('%y') # Year
        cursor.execute("""
            SELECT MAX(invoice_no) FROM sales 
            WHERE invoice_no LIKE %s
        """, (f'TKB/{current_month}%/{current_year}',))

        last_invoice = cursor.fetchone()[0]

        if last_invoice:
            parts = last_invoice.split('/')
            number = int(parts[1][2:]) + 1
            return f"TKB/{current_month}{number:03d}/{current_year}"

        return f"TKB/{current_month}001/{current_year}"
    except Exception as e:
        print(f"Error getting next invoice number: {e}")
        return f"TKB/{current_month}001/{current_year}"
    finally:
        cursor.close()
        conn.close()


# Display products function
def read_product_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT product FROM sales ORDER BY product;")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error reading product names: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# Display categories function
def read_categories():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT DISTINCT category FROM sales ORDER BY category;")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error reading client names: {e}")
        return []
    finally:
        cursor.close
        conn.close


# Display account owners function
def read_account_owners():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT DISTINCT account_owner FROM sales ORDER BY account_owner;")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error reading client names: {e}")
        return []
    finally:
        cursor.close
        conn.close


# Display clients function
def read_client_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT customer_name FROM clients ORDER BY customer_name;")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error reading client names: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# Password validation page
def validate_password(password):
    """
    Password validation:
    - Must contain at least 8 characters
    - Contains uppercase, lowercase, a number, and a special symbol
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number."

    if not re.search(r"[!@#$%^&*()?\":{}|<>]", password):
        return "Password must contain at least one special symbol (!@#$%^&*)."


# Generate Receipt function
def generate_receipt(sales_id, customer_name, invoice_no, amount_paid, new_bal, payment_date, items):

    os.makedirs(app.config['RECEIPT_FOLDER'], exist_ok=True)
    sanitized_invoice_no = re.sub(r'[^a-zA-Z0-9]', '_', invoice_no)
    filename = f"receipt_{sanitized_invoice_no}.pdf"
    filepath = os.path.join(app.config['RECEIPT_FOLDER'], filename)

    c = canvas.Canvas(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]

    # Company information
    address = "Brightwoods Apartment, Chania Ave"
    city_state_zip = "PO. Box 74080-00200, Nairobi, KENYA"
    phone = "Phone: +254-705917383"
    email = "Email: info@teknobyte.ltd"
    kra_pin = "PIN: P051155522R"

    c.setFont("Helvetica", 8)
    c.drawString(430, 740, "")
    c.drawString(430, 730, address)
    c.drawString(430, 720, city_state_zip)
    c.drawString(430, 710, phone)
    c.drawString(430, 700, email)
    c.drawString(430, 690, kra_pin)
    c.drawString(430, 660, "")

    # Receipt title and payment details
    c.setFont("Helvetica-Bold", 20)
    c.drawString(250, 640, "Receipt")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 600, f"Date: {payment_date.strftime('%d-%m-%Y')}")
    c.drawString(50, 580, f"Invoice No: {invoice_no}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 560, f"Client: {customer_name}")

    # Items table
    data = [
        ['Description', 'Qty', 'Unit Price', 'Amount']
    ]
    for item in items:
        data.append([
            item['description'],
            str(item['quantity']),
            f"Ksh {item['unit_price']:,.1f}",
            f"Ksh {item['total']:,.1f}"
        ])

    table = Table(data, colWidths=[3 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    table_height = len(data) * 20
    table.wrapOn(c, 0, 0)
    table.drawOn(c, 50, 500 - table_height)

    # Payment details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, 480 - table_height, f"Paid: Ksh {amount_paid:,.1f}")

    # Payment status (Paid or Balance remaining)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, 460 - table_height, f"Balance: Ksh {new_bal:,.1f}")

    # Accountant details
    c.setFont("Helvetica", 12)
    c.drawString(50, 200, "John Kungu")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 180, "ACCOUNTANT")

    c.save()
    with open(filepath, 'rb') as f:
        receipt_buffer = BytesIO(f.read())
    receipt_buffer.seek(0)
    return receipt_buffer


# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'] # Get the name from the form
        password = request.form['password'] # Get the password from the form

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT user_id, role, username, password, status FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            if user[4] == 'Inactive':
                flash('Your account is inactive you cannot login', 'danger')
                return render_template('login.html')

            if user and check_password_hash(user[3], password):
                session['user_id'] = user[0]
                session['role'] = user[1]
                session['username'] = user[2]

                if user[1] == 1:
                    return redirect(url_for('superuser_dashboard'))
                elif user[1] == 2:
                    return redirect(url_for('admin_dashboard'))
                elif user[1] == 3:
                    return redirect(url_for('user_dashboard'))

        flash("Invalid credentials!", "danger")
    return render_template('login.html')


# User dashboard route
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session or session.get('role') != 3: # Redirect to login if not user
        return redirect(url_for('login'))

    return render_template('user_dashboard.html')


# Admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 2:
        return redirect(url_for('login'))

    return render_template('admin_dashboard.html')


# Superuser dashboard route
@app.route('/superuser_dashboard')
def superuser_dashboard():
    if 'user_id' not in session or session.get('role') != 1:
        return redirect(url_for('login'))
    return render_template('superuser_dashboard.html')


# Sales Menu route
@app.route('/sales')
def sales_menu():
    return render_template('sales_menu.html')


# Sales reports menu route
@app.route('/sales/reports')
def sales_reports_menu():
    return render_template('sales_reports_menu.html')


# Sales entry route
@app.route('/sales/entry', methods=['GET', 'POST'])
def sales_entry():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'search_client':
            client_name = request.form.get('client_name')
            found_clients = [name for name in read_client_names() if client_name.lower() in name.lower()]

            if not found_clients:
                return jsonify({'status': 'not_found'})
            elif len(found_clients) == 1:
                return jsonify({
                    'status': 'single_result',
                    'client_name': found_clients[0]
                })
            else:
                return jsonify({
                    'status': 'multiple_results',
                    'clients': found_clients[:10]  # Limit to 10 results
                })

        elif action == 'select_client':
            client_name = request.form.get('client_name')
            return jsonify({
                'status': 'success',
                'client_name': client_name,
                'invoice_number': get_next_invoice_number(),
                'current_date': get_current_date()
            })

        elif action == 'save_sale':
            try:
                # Get form data
                invoice_date = datetime.strptime(request.form.get('invoice_date'), '%Y-%m-%d')
                invoice_number = request.form.get('invoice_number')
                customer_name = request.form.get('client_name')
                product = request.form.get('product')
                quantity = int(request.form.get('quantity'))
                price = float(request.form.get('price'))
                category = request.form.get('category')
                account_owner = request.form.get('account')
                notes = request.form.get('notes', '')
                transaction_type = request.form.get('transaction_type')  # 'sell' or 'take_back'
                add_another = request.form.get('add_another', 'no') == 'yes'

                # Adjust quantity based on transaction type
                if transaction_type == 'take_back':
                    quantity = -abs(quantity)  # quantity is negative for take back

                # Calculation of Values
                total = round(quantity * price, 2)
                paid = 0
                balance = total
                paid_date = None
                acc_status = 'Active'
                payment_status = 'Not Paid'

                current_datetime = get_current_datetime()

                # Save to database
                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO sales (
                        invoice_date, invoice_no, customer_name, product, qty, 
                        amt, total, paid, bal, paid_date, category, 
                        account_owner, acc_status, payment_status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING sales_id;
                """, (
                    invoice_date, invoice_number, customer_name, product, quantity,
                    price, total, paid, balance, paid_date, category,
                    account_owner, acc_status, payment_status
                ))

                sale_id = cursor.fetchone()[0]
                conn.commit()

                cursor.execute("""
                    SELECT product as description, qty as quantity, 
                           amt as unit_price, total as total
                    FROM sales 
                    WHERE invoice_no = %s
                    ORDER BY sales_id
                """, (invoice_number,))

                columns = [desc[0] for desc in cursor.description]
                all_items = []
                for row in cursor.fetchall():
                    all_items.append(dict(zip(columns, row)))

                # Generate invoice PDF
                invoice_data = {
                    'customer_name': customer_name,
                    'invoice_number': invoice_number,
                    'invoice_date': invoice_date.strftime('%d-%m-%Y'),
                    'items': [{
                        'description': item['description'],
                        'quantity': item['quantity'],
                        'unit_price': item['unit_price'],
                        'total': item['total'],
                    } for item in all_items],
                    'total_amount': sum(item['total'] for item in all_items),
                    'notes': notes,
                    'payment_status': payment_status
                }

                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                sanitized_invoice_no = re.sub(r'[^a-zA-Z0-9]', '_', invoice_number)
                filename = f"invoice_{sanitized_invoice_no}.pdf"
                create_invoice(invoice_data, os.path.join(app.config['UPLOAD_FOLDER'], filename))

                response = {
                    'status': 'success',
                    'message': 'Sales saved successfully!',
                    'invoice_url': url_for('download_invoice', filename=filename),
                    'invoice_number': invoice_number
                }

                if add_another:
                    # Prepare data for next entry
                    return jsonify({
                        'status': 'add_another',
                        'message': 'Sale added successfully! Add another item?',
                        'invoice_number': invoice_number,
                        'client_name': customer_name,
                        'invoice_date': invoice_date,
                        'invoice_url': url_for('download_invoice', filename=filename),
                        'current_items': all_items
                    })
                else:
                    return jsonify({
                        'status': 'success',
                        'message': 'Sales saved successfully!',
                        'invoice_url': url_for('download_invoice', filename=filename),
                        'invoice_number': invoice_number
                    })

            except Exception as e:
                conn.rollback()
                return jsonify({
                    'status': 'error',
                    'message': f'An error occurred: {str(e)}'
                }), 500
            finally:
                cursor.close()
                conn.close()

    # GET request - show the form
    product_names = read_product_names()
    next_invoice_number = get_next_invoice_number()
    categories = read_categories()
    accounts = read_account_owners()
    client_names = read_client_names()

    # Initialize customer name and invoice number from query parameters if they exist
    customer_name = request.args.get('customer_name', '')
    invoice_number = request.args.get('invoice_number', next_invoice_number)
    date_created = datetime.today().strftime('%d-%m-%Y')

    return render_template('sales_entry.html',
                           product_names=product_names,
                           next_invoice_number=invoice_number,
                           customer_name=customer_name,
                           categories=categories,
                           accounts=accounts,
                           client_names=client_names,
                           current_date=get_current_date(),
                           date_created=date_created)


# Download invoice route
@app.route('/invoices/<filename>')
def download_invoice(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )


# Download receipt route
@app.route('/download_receipt/<int:sales_id>')
def download_receipt(sales_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM sales WHERE sales_id = %s", (sales_id,))
    invoice = cur.fetchone()

    if not invoice:
        flash("Invoice not found", "danger")
        return redirect(url_for('search_invoices'))

    # Extract fields from the invoice row
    customer_name = invoice[3]
    invoice_no = invoice[2]
    product = invoice[6]
    quantity = invoice[7]
    amount = invoice[8]
    paid = invoice[10]
    balance = invoice[11]

    sanitized_invoice_no = re.sub(r'[^a-zA-Z0-9]', '_', invoice_no)
    filename = f"receipt_{sanitized_invoice_no}.pdf"
    filepath = os.path.join(app.config['RECEIPT_FOLDER'], filename)

    if not os.path.exists(filepath):

        receipt_buffer = generate_receipt(
            sales_id = sales_id,
            customer_name = customer_name,
            invoice_no = invoice_no,
            amount_paid = paid,
            new_bal = balance,
            payment_date = datetime.now().date(),
            items=[{
                'description': product,
                'quantity': int(quantity),
                'unit_price': float(amount),
                'total': int(quantity) * float(amount)
            }]
        )
        flash("Receipt generated for download", "info")
    else:
        # Read existing receipt
        with open(filepath, 'rb') as f:
            receipt_buffer = BytesIO(f.read())
        receipt_buffer.seek(0)

    # Prepare download
    response = make_response(receipt_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

# Search invoices route
@app.route('/search_invoices', methods=['GET', 'POST'])
def search_invoices():
    invoices = []
    customers = []
    categories = []
    products = []

    # Set default date range
    today = datetime.today()
    default_start_date = (today - timedelta(days=730)).strftime('%Y-%m-%d')
    default_end_date = (today + timedelta(days=7)).strftime('%Y-%m-%d')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch dropdown values
        cur.execute("SELECT DISTINCT customer_name FROM sales ORDER BY customer_name;")
        customers = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT DISTINCT category FROM sales ORDER BY category;")
        categories = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT DISTINCT product FROM sales ORDER BY product;")
        products = [row[0] for row in cur.fetchall()]

        if request.method == 'POST':
            start_date = request.form.get('start_date') or default_start_date
            end_date = request.form.get('end_date') or default_end_date
            customer_name = request.form.get('customer_name')
            category = request.form.get('category')
            product = request.form.get('product')

            # Start building query
            query = """
                       SELECT sales_id, invoice_date, invoice_no, customer_name, 
                              product, qty, total, payment_status, category
                       FROM sales
                       WHERE 1=1
                   """
            params = []

            # Apply filters only if they are selected
            if start_date:
                query += " AND invoice_date >= %s"
                params.append(start_date)

            if end_date:
                query += " AND invoice_date <= %s"
                params.append(end_date)

            if customer_name:
                query += " AND customer_name = %s"
                params.append(customer_name)

            if category:
                query += " AND category = %s"
                params.append(category)

            if product:
                query += " AND product = %s"
                params.append(product)

            query += " ORDER BY invoice_date DESC"

            cur.execute(query, tuple(params))
            invoices = cur.fetchall()

            if not invoices:
                flash('No invoices found matching the selected filters.', 'info')

        cur.close()
        conn.close()

    except Exception as e:
        return render_template('search_invoices.html',
                               error=f"Database error: {str(e)}",
                               invoices=invoices,
                               customers=customers,
                               categories=categories,
                               products=products,
                               default_start_date=default_start_date,
                               default_end_date=default_end_date)

    return render_template('search_invoices.html',
                           invoices=invoices,
                           customers=customers,
                           categories=categories,
                           products=products,
                           default_start_date=default_start_date,
                           default_end_date=default_end_date)


# Update payment
@app.route('/update_payment/<int:sales_id>', methods=['GET', 'POST'])
def update_payment(sales_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Verify if it is superuser and fetch invoice
    if session.get('role') != 1:  # If not superuser
        cur.close()
        conn.close()
        flash("You don't have permission to edit payments", "danger")
        return redirect(url_for('search_invoices'))

    cur.execute("SELECT * FROM sales WHERE sales_id = %s", (sales_id,))
    invoice = cur.fetchone()

    if not invoice:
        flash("Invoice not found or access denied", "danger")
        return redirect(url_for('search_invoices'))

    if request.method == 'POST':
        invoice_date = request.form['invoice_date']
        invoice_no = request.form['invoice_no']
        customer_name = request.form['customer_name']
        product = request.form['product']
        quantity = request.form['quantity']
        amount = float(request.form['amount'])
        total =float(request.form['total'])
        paid = float(request.form['paid'])
        balance = float(max(0, total - paid))
        paid_date = datetime.now().date() if balance == 0 else None # Only update when balance is zero
        category = request.form['category']
        account_owner = request.form['account_owner']
        payment_status = 'Paid' if balance == 0 else 'Not Paid' # Set Paid if there is no balance
        try:
            # Update invoice
            cur.execute("""
                UPDATE sales SET
                invoice_date = %s,
                invoice_no = %s,
                customer_name = %s,
                product = %s,
                qty = %s,
                amt = %s,
                total = %s,
                paid = %s,
                bal = %s,
                paid_date = CASE WHEN %s = 0 THEN CURRENT_DATE ELSE paid_date END,
                category = %s,
                account_owner = %s,
                payment_status = %s
                WHERE sales_id = %s
            """, (
                invoice_date,
                invoice_no,
                customer_name,
                product,
                quantity,
                amount,
                total,
                paid,
                balance,
                balance,
                category,
                account_owner,
                payment_status,
                sales_id
            ))
            conn.commit()
            if paid > 0:
                generate_receipt(
                    sales_id=sales_id,
                    customer_name=customer_name,
                    invoice_no=invoice_no,
                    amount_paid=paid,
                    new_bal=balance,
                    payment_date=datetime.now().date(),
                    items=[{
                        'description': product,
                        'quantity': quantity,
                        'unit_price': amount,
                        'total': total
                    }]
                )
            return redirect(url_for('view_sales', sales_id=sales_id))

        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}", "danger")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for('search_invoices'))

    return render_template('update_payment.html', invoice=invoice)


# View sales route
@app.route('/invoice/<int:sales_id>')
def view_sales(sales_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales WHERE sales_id = %s", (sales_id,))
    invoice = cur.fetchone()
    cur.close()
    conn.close()

    if not invoice:
        flash("Invoice not found", "danger")
        return redirect(url_for('search_invoices'))

    return render_template('view_sales.html', invoice=invoice)


# Manage users route
@app.route('/manage_users')
def manage_users():
    if 'user_id' not in session or session.get('role') not in [1,2]:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.user_id, u.username, r.role_name, u.status 
        FROM users u 
        JOIN roles r ON u.role = r.role_id
        ORDER BY u.user_id ASC
    """)
    users = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('manage_users.html', users=users)


# Add users route
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session or session.get('role') not in [1, 2]:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT role_id, role_name FROM roles")
    roles = cur.fetchall()

    if request.method == 'POST':
        username = request.form['username']
        role_id = request.form['role']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        error = validate_password(password)
        if error:
            flash(error, "danger")
            selected_role = int(role_id)
            return render_template('add_users.html', roles=roles, username=username, selected_role=selected_role)

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            selected_role = int(role_id)
            return render_template('add_users.html', roles=roles, username=username, selected_role=selected_role)

        hashed_password = generate_password_hash(password)

        try:
            cur.execute("""
                INSERT INTO users (username, role, password) 
                VALUES (%s, %s, %s)
            """, (username, role_id, hashed_password))
            conn.commit()
            flash('User added successfully!', 'success')

            # Redirect to manage users page
            return redirect(url_for('manage_users'))

        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return render_template('add_users.html', roles=roles, username=username, selected_role=role_id)

        finally:
            cur.close()
            conn.close()
    else:
        # GET: fetch roles for dropdown
        cur.execute("SELECT role_id, role_name FROM roles")
        roles = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('add_users.html', roles=roles)


# Change Password Route
@app.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
def change_password(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session['user_id'] != user_id:
        flash("You can only change your own password.", "danger")
        return redirect(url_for('manage_users'))

    if request.method == 'POST':
        user_id = session['user_id']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        error = validate_password(new_password)
        if error:
            flash(error, "danger")
            return redirect(url_for('change_password'))
        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('change_password', user_id=user_id))

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT password FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()

        if user and check_password_hash(user[0], old_password):
            hashed_password = generate_password_hash(new_password)
            cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (hashed_password, user_id))
            conn.commit()
            flash('Password changed successfully!', 'success')
        else:
            flash('Old password is incorrect!', 'danger')

        cur.close()
        conn.close()

        return redirect(url_for('change_password', user_id=user_id))

    return render_template('change_password.html')


# User details route
@app.route('/user_details/<int:user_id>')
def user_details(user_id):
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if session.get('role') == 1 or session.get('role') == 2:
            cur.execute("""
            SELECT u.user_id, u.username, r.role_name FROM users u
            JOIN roles r
            ON u.role = r.role_id
            WHERE u.user_id = %s
            """, (user_id,))
        else:
            cur.execute("""
            SELECT u.user_id, u.username, r.role_name FROM users u
            JOIN roles r
            ON u.role = r.role_id
            WHERE u.user_id = %s
            AND u.user_id = %s
            """, (user_id, session['user_id']))

        user = cur.fetchone()

        if not user:
            flash("User not found or access denied.", "danger")
            return redirect(url_for('manage_users'))

        return render_template('user_details.html', user=user)
    
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('manage_users'))
    finally:
        cur.close()
        conn.close()


# Edit User information route
@app.route('/edit_users/<int:user_id>', methods=['GET', 'POST'])
def edit_users(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if session.get('role') not in [1, 2]:
        flash('Access denied', 'danger')
        return redirect(url_for('manage_users'))

    if request.method == 'POST':
        # Get data from form
        username = request.form.get('username')
        role_id = request.form.get('role')
        status = request.form.get('status')

        try:
            # Update user in the database
            cur.execute("""
                UPDATE users
                SET username = %s, role = %s, status = %s
                WHERE user_id = %s
            """, (username, role_id, status, user_id))
            conn.commit()
            flash("User updated successfully", "success")
            return redirect(url_for('manage_users'))
        except Exception as e:
            conn.rollback()
            flash(f"Failed to update user: {e}", "danger")
        finally:
            cur.close()
            conn.close()
    else:
        try:
            # Fetch user details
            cur.execute(""" 
                SELECT u.user_id, u.username, r.role_id, r.role_name, u.status 
                FROM users u 
                JOIN roles r ON u.role = r.role_id
                WHERE u.user_id = %s
            """, (user_id,))
            user = cur.fetchone()

            # Fetch all roles for the dropdown
            cur.execute("SELECT role_id, role_name FROM roles")
            roles = cur.fetchall()

            if not user:
                flash("User not found or access denied", "danger")
                return redirect(url_for('manage_users'))

            return render_template('edit_users.html', user=user, roles=roles)

        except Exception as e:
            flash(f"Error fetching user: {e}", "danger")
            return redirect(url_for('manage_users'))
        finally:
            cur.close()
            conn.close()


# Manage Clients
@app.route('/manage_clients')
def manage_clients():
    if 'user_id' not in session or session.get('role') not in [1,2]:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients ORDER BY customer_name ASC")
    clients = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('manage_clients.html', clients=clients)


# Add new client route
@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if 'user_id' not in session or session.get('role') not in [1, 2]:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        institution = request.form['institution']
        phone_no = request.form['phone_no']
        phone_no_2 = request.form['phone_no_2']
        email = request.form['email']
        position = request.form['position']
        id_no = request.form['id_no']
        date_created = datetime.today() # Today's date is used by default


        try:
            # Check if the client already exists
            cur.execute("SELECT * FROM clients WHERE phone_no = %s", (phone_no,))
            existing_client = cur.fetchone()

            if existing_client:
                flash("Client already exists!", "warning")
            else:
                cur.execute("""
                    INSERT INTO clients (customer_name, institution, phone_no, phone_no_2, email, position, id_no, date_created) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (customer_name, institution, phone_no, phone_no_2, email, position, id_no, date_created))
                conn.commit()
                flash('Client added successfully!', 'success')

            return redirect(url_for('manage_clients'))

        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')

        finally:
            cur.close()
            conn.close()
    else:
        return render_template('add_clients.html')


# Add client via modal AJAX route
@app.route('/add_client_ajax', methods=['POST'])
def add_client_ajax():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'})

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        customer_name = request.form['customer_name']
        institution = request.form['institution']
        phone_no = request.form['phone_no']
        phone_no_2 = request.form['phone_no_2']
        email = request.form['email']
        position = request.form['position']
        id_no = request.form['id_no']
        date_created = datetime.today() # Today's date is used by default

        # Check if client already exists
        cur.execute("SELECT * FROM clients WHERE phone_no = %s", (phone_no,))
        existing_client = cur.fetchone()

        if existing_client:
            return jsonify({'success': False, 'error': 'Client with this phone number already exists.'})
        else:
            cur.execute("""
                INSERT INTO clients (customer_name, institution, phone_no, phone_no_2, email, position, id_no, date_created) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (customer_name, institution, phone_no, phone_no_2, email, position, id_no, date_created))
            conn.commit()

            return jsonify({'success': True, 'customer_name': customer_name})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})

    finally:
        cur.close()
        conn.close()


# Edit client info route
@app.route('/edit_clients/<int:customer_id>', methods=['GET', 'POST'])
def edit_clients(customer_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if session.get('role') not in [1, 2]:
        flash('Access denied', 'danger')
        return redirect(url_for('manage_clients'))

    if request.method == 'POST':
        # Get data from form
        customer_name = request.form.get('customer_name')
        institution = request.form.get('institution')
        phone_no = request.form.get('phone_no')
        phone_no_2 = request.form.get('phone_no_2')
        email = request.form.get('email')
        position = request.form.get('position')
        id_no = request.form.get('id_no')

        try:
            # Update user in the database
            cur.execute("""
                UPDATE clients
                SET customer_name = %s, institution = %s, phone_no = %s, phone_no_2 = %s,
                email = %s, position = %s, id_no = %s
                WHERE customer_id = %s
            """, (customer_name, institution, phone_no, phone_no_2, email, position, id_no, customer_id))
            conn.commit()
            flash("Client updated successfully", "success")
            return redirect(url_for('manage_clients'))
        except Exception as e:
            conn.rollback()
            flash(f"Failed to update client: {e}", "danger")
        finally:
            cur.close()
            conn.close()
    else:
        cur.execute("SELECT * FROM clients WHERE customer_id = %s", (customer_id,))
        client = cur.fetchone()
        cur.close()
        conn.close()

        if client:
            return render_template('edit_clients.html', client=client)
        else:
            flash("Client not found", "danger")
            return redirect(url_for('manage_clients'))


# View invoice preview route
@app.route('/sales/view/<invoice_number>')
def view_invoice(invoice_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM sales 
            WHERE invoice_no = %s
            ORDER BY sales_id
        """, (invoice_number,))

        sales_items = cursor.fetchall()
        if not sales_items:
            return "Invoice not found", 404

        # Generate filename from invoice number
        sanitized_invoice_no = re.sub(r'[^a-zA-Z0-9]', '_', invoice_number)
        filename = f"invoice_{sanitized_invoice_no}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Check if PDF already exists
        if not os.path.exists(filepath):
            # Create invoice data structure
            invoice_data = {
                'customer_name': sales_items[0][3],  # customer_name
                'invoice_number': invoice_number,
                'invoice_date': sales_items[0][1],  # invoice_date
                'items': [{
                    'description': item[6],  # product
                    'quantity': item[7],  # qty
                    'unit_price': item[8],  # amt
                    'total': item[9]  # total
                } for item in sales_items],
                'total_amount': sum(item[9] for item in sales_items),
                'notes': sales_items[0][10] or '',  # notes
                'payment_status': sales_items[0][18]  # payment_status
            }
            create_invoice(invoice_data, filepath)

        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            filename,
            as_attachment=False
        )
    except Exception as e:
        return f"Error generating invoice: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()


# Generate invoice route
def create_invoice(invoice_data, filename):
    # Create canvas
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Create style
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]

    # Company information
    address = "Brightwoods Apartment, Chania Ave"
    city_state_zip = "PO. Box 74080-00200, Nairobi, KENYA "
    phone = "Phone: +254-705917383"
    email = "Email: info@teknobyte.ltd"
    kra_pin = "PIN: P051155522R"

    c.setFont("Helvetica", 8)
    c.drawString(430, 740, "")
    c.drawString(430, 730, address)
    c.drawString(430, 720, city_state_zip)
    c.drawString(430, 710, phone)
    c.drawString(430,700,email)
    c.drawString(430, 690, kra_pin)
    c.drawString(430, 660, "")
    
    # Invoice title and details
    c.setFont("Helvetica-Bold", 20)
    c.drawString(280, 640, "Invoice")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 620, "")
    c.drawString(50, 600, f"Date: {invoice_data['invoice_date']}")
    invoice_label = "Invoice No:"
    invoice_number = invoice_data['invoice_number']
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 580, invoice_label)
    label_width = c.stringWidth(invoice_label, "Helvetica-Bold", 12)
    c.setFont("Helvetica", 12)
    c.drawString(50 + label_width + 5, 580, invoice_number)

    # Customer information
    c.drawString(50, 560, "")
    client_label = "Client: "
    client_name = invoice_data['customer_name']
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 540, client_label)

    label_width = c.stringWidth(client_label, "Helvetica-Bold", 12)
    
    # Client name next to the label
    c.setFont("Helvetica", 12)
    c.drawString(50 + label_width + 5, 540, client_name)

    # Items table
    data = [
        ['Description', 'Qty', 'Unit Price', 'Amount']
    ]
    for item in invoice_data['items']:
        data.append([
            item['description'],
            str(item['quantity']),
            f"Ksh {item['unit_price']:,.1f}",
            f"Ksh {item['total']:,.1f}"
        ])

    table = Table(data, colWidths=[3 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    table_height = len(data) * 20
    table.wrapOn(c, 0, 0)
    table.drawOn(c, 50, 500 - table_height)

    # Add total amount
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, 480 - table_height, f"Total Amount: {invoice_data['total_amount']:,.1f}")

    # Notes section
    if invoice_data['notes']:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 360, "Notes:")
        c.setFont("Helvetica", 10)
        notes = Paragraph(invoice_data['notes'].replace('\n', '<br/>'),
                          ParagraphStyle(name='Normal', alignment=TA_LEFT, parent= style_normal, fontName='Helvetica', fontSize=10, leading=14))
        w, h = notes.wrap(400, 100)
        notes.drawOn(c, 50, 340 - h)

    # Accountant details
    c.setFont("Helvetica", 12)
    c.drawString(50, 200, "John Kungu")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 180, "ACCOUNTANT")
    c.save()


# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))


@app.route('/payments')
def payments_menu():
    return render_template('payments_menu.html')


@app.route('/search_billing_account', methods=['GET', 'POST'])
def search_billing_account():
    if request.method == 'GET' and ('term' in request.args or 'all' in request.args):
        search_term = request.args.get('term', '').strip()
        show_all = request.args.get('all', 'false').lower() == 'true'
        print(f"Search term received: {search_term}, Show all: {show_all}")

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Main query
            query = sql.SQL("""
                SELECT service_provider, account_name, account_number, category, paybill_number, ussd_number,
                       frequency, billing_date, bill_amount, account_owner, created_date, invoice_number,
                       status, bank_account
                FROM billing_account
            """)

            # Add WHERE clause only if not showing all and search term exists
            if not show_all and search_term:
                query = sql.SQL("""
                    {base_query}
                    WHERE account_name ILIKE %s OR service_provider ILIKE %s
                """).format(base_query=query)
                params = (f'%{search_term}%', f'%{search_term}%')
            else:
                params = ()

            # Add ordering and limit
            query = sql.SQL("""
                {base_query}
                ORDER BY account_name
                LIMIT 100
            """).format(base_query=query)

            cur.execute(query, params)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            results = []
            for idx, row in enumerate(rows):
                print(f"Row {idx}: {row}")
                # Safely handle billing_date formatting
                billing_date = ''
                try:
                    billing_date = row[7].strftime('%Y-%m-%d') if hasattr(row[7], 'strftime') else str(row[7])
                except Exception as e:
                    print(f"Date formatting error: {e}")
                    billing_date = str(row[7])

                results.append({
                    'label': f"{row[1]} ({row[0]})",
                    'value': row[1],  # account_name
                    'data': {
                        'service_provider': row[0],
                        'account_name': row[1],
                        'account_number': row[2],
                        'category': row[3],
                        'paybill_number': row[4],
                        'ussd_number': row[5],
                        'frequency': row[6],
                        'billing_date': billing_date,
                        'bill_amount': row[8],
                        'account_owner': row[9],
                        'created_date': row[10],
                        'invoice_number': row[11],
                        'status': row[12],
                        'bank_account': row[13]
                    }
                })
            return jsonify(results)
        except Exception as e:
            print(f"Database error: {e}")
            return jsonify([])

    elif request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'edit':
            try:
                # Get all form data
                invoice_number = request.form['invoice_number']
                service_provider = request.form['service_provider']
                account_name = request.form['account_name']
                account_number = request.form['account_number']
                category = request.form['category']
                paybill_number = request.form['paybill_number']
                ussd_number = request.form['ussd_number']
                frequency = request.form['frequency']
                billing_date = request.form['billing_date']
                bill_amount = request.form['bill_amount']
                account_owner = request.form['account_owner']
                status = request.form.get('status', 'Active')  # Default to Active if not provided
                bank_account = request.form['bank_account']
                conn = get_db_connection()
                cur = conn.cursor()

                # Update query

                update_query = sql.SQL("""

                        UPDATE billing_account
                        SET 
                            service_provider = %s,
                            account_name = %s,
                            account_number = %s,
                            category = %s,
                            paybill_number = %s,
                            ussd_number = %s,
                            frequency = %s,
                            billing_date = %s,
                            bill_amount = %s,
                            account_owner = %s,
                            status = %s,
                            bank_account = %s
                        WHERE invoice_number = %s
                        RETURNING *
                    """)

                cur.execute(update_query, (
                    service_provider,
                    account_name,
                    account_number,
                    category,
                    paybill_number,
                    ussd_number,
                    frequency,
                    billing_date,
                    bill_amount,
                    account_owner,
                    status,
                    bank_account,
                    invoice_number
                ))

                # Get the updated record
                updated_record = cur.fetchone()
                conn.commit()
                # Format the updated record for response

                billing_date = ''
                try:
                    billing_date = updated_record[7].strftime('%Y-%m-%d') if hasattr(updated_record[7],
                                                                          'strftime') else str(
                        updated_record[7])
                except Exception as e:
                    print(f"Date formatting error: {e}")
                    billing_date = str(updated_record[7])

                updated_data = {

                    'service_provider': updated_record[0],
                    'account_name': updated_record[1],
                    'account_number': updated_record[2],
                    'category': updated_record[3],
                    'paybill_number': updated_record[4],
                    'ussd_number': updated_record[5],
                    'frequency': updated_record[6],
                    'billing_date': billing_date,
                    'bill_amount': updated_record[8],
                    'account_owner': updated_record[9],
                    'created_date': updated_record[10],
                    'invoice_number': updated_record[11],
                    'status': updated_record[12],
                    'bank_account': updated_record[13]
                }

                return jsonify({

                    'success': True,
                    'message': 'Billing account updated successfully',
                    'updated_data': updated_data
                })
            except Exception as e:
                print(f"Error updating billing account: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Failed to update billing account: {str(e)}'
                }), 400
            finally:
                cur.close()
                conn.close()

        elif form_type == 'add':
            try:
                # Get form fields
                service_provider = request.form['service_provider']
                account_name = request.form['account_name']
                account_number = request.form['account_number']
                category = request.form['category']
                paybill_number = request.form['paybill_number']
                ussd_number = request.form['ussd_number']
                frequency = request.form['frequency']
                billing_date = request.form['billing_date']
                bill_amount = request.form['bill_amount']
                account_owner = request.form['account_owner']
                status = request.form.get('status', 'Active')
                bank_account = request.form['bank_account']

                # Generate invoice number
                invoice_number = generate_next_invoice_number()

                conn = get_db_connection()
                cur = conn.cursor()
                insert_query = sql.SQL("""
                            INSERT INTO billing_account (
                                service_provider, account_name, account_number, category, paybill_number, 
                                ussd_number, frequency, billing_date, bill_amount, account_owner, 
                                status, bank_account, invoice_number
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING invoice_number, created_date
                        """)
                cur.execute(insert_query, (
                    service_provider, account_name, account_number, category, paybill_number,
                    ussd_number, frequency, billing_date, bill_amount, account_owner,
                    status, bank_account, invoice_number
                ))
                result = cur.fetchone()
                conn.commit()

                return jsonify({
                    'success': True,
                    'message': 'Billing account added successfully',
                    'invoice_number': invoice_number,  # Use the generated number
                    'created_date': result[1].strftime('%Y-%m-%d')
                })
            except Exception as e:
                print(f"Error adding billing account: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Failed to add billing account: {str(e)}'
                }), 400
            finally:
                cur.close()
                conn.close()
        return jsonify({'success': False, 'message': 'Invalid form type'}), 400
    return render_template('billing-accounts/search-billing-account.html')


@app.route('/edit_billing_account')
def edit_billing_account():
    return render_template('billing-accounts/edit-billing-account.html')


@app.route('/add_billing_account')
def add_billing_account():
    return render_template('billing-accounts/add-billing-account.html')


def generate_next_invoice_number():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get current month and year
    now = datetime.now()
    month = f"{now.month:02d}"
    year_short = f"{now.year % 100:02d}"

    # Find the highest existing invoice number for this month/year
    cur.execute(
        sql.SQL("SELECT invoice_number FROM invoices WHERE invoice_number LIKE %s ORDER BY id DESC LIMIT 1"),
        [f"TKB/{month}%/{year_short}"]
    )
    last_invoice = cur.fetchone()

    if last_invoice:
        # Extract the numeric part (e.g., "042" from "TKB/05042/25")
        last_seq = int(last_invoice[0].split("/")[1][2:])  # Split and take digits after MM
        next_seq = last_seq + 1
    else:
        # No invoices for this month/year yet; start at 1
        next_seq = 1

    # Format the next invoice number (3-digit sequence)
    invoice_number = f"TKB/{month}{next_seq:03d}/{year_short}"

    # Save to database (with error handling for race conditions)
    try:
        cur.execute(
            sql.SQL("INSERT INTO invoices (invoice_number) VALUES (%s)"),
            [invoice_number]
        )
        conn.commit()
    except errors.UniqueViolation:
        # Race condition: retry once if another request created the same invoice
        conn.rollback()
        return generate_next_invoice_number()
    finally:
        cur.close()
        conn.close()

    return invoice_number


@app.route('/get_next_invoice_number')
def get_next_invoice_number():
    invoice_number = generate_next_invoice_number()
    return {'invoice_number': invoice_number}


# Allow external hosting
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RECEIPT_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
