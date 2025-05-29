# import appropriate libraries
from flask import Flask,flash, session, render_template, request, redirect, url_for, send_from_directory, jsonify, make_response
import os
import io
from io import BytesIO
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
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

# Display products function
def read_product_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT product FROM products ORDER BY product;")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error reading product names: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# Display categories function
def read_categories():
    return [
        "Books",
        "Consultancy",
        "Rent",
    ]
# Display account owners function
def read_account_owners():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT DISTINCT account_owner FROM account_owner ORDER BY account_owner;")
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

# Bank Accounts function
def read_bank_accounts():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT account_name || '-' || bank_name FROM banks ORDER BY account_name;") # Concatenation of the account name and bank name
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error reading bank accounts: {e}")
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
    if 'user_id' not in session or session.get('role') != 3: # Redirect to login page if not user
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
                    'clients': found_clients[:10]
                })

        elif action == 'select_client':
            client_name = request.form.get('client_name')
            return jsonify({
                'status': 'success',
                'client_name': client_name,
                'invoice_number': generate_next_invoice_number(),
                'current_date': get_current_date()
            })

        elif action == 'save_sale':
            conn = None
            cursor = None
            try:
                invoice_date = datetime.strptime(request.form.get('invoice_date'), '%Y-%m-%d')
                invoice_number = request.form.get('invoice_number')
                customer_name = request.form.get('client_name')
                product = request.form.get('product')
                quantity = int(request.form.get('quantity'))
                price = float(request.form.get('price'))
                category = request.form.get('category')
                account_owner = request.form.get('account')
                date_created = datetime.now()
                notes = request.form.get('notes', '')
                transaction_type = request.form.get('transaction_type')
                add_another = request.form.get('add_another', 'no') == 'yes'
                bank_account = request.form.get('bank_account', '')

                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("SELECT frequency FROM products WHERE product = %s", (product,))
                product_frequency = cursor.fetchone()
                if product_frequency is None:
                    return jsonify({'status': 'error', 'message': f'Product "{product}" not found in database'}), 400

                frequency = product_frequency[0] if product_frequency else 'Occasional'
                sales_acc_invoice_no = None

                if transaction_type == 'take_back':
                    quantity = -abs(quantity)

                total = round(quantity * price, 2)
                current_datetime = datetime.now()

                # Handle occasional products (immediate sale)
                if frequency == 'Occasional':
                    cursor.execute("""
                        INSERT INTO sale (
                            invoice_date, invoice_no, customer_name, product, quantity, 
                            price, total, date_created, category, account_owner, 
                            sales_acc_invoice_no, bank_account
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        invoice_date, invoice_number, customer_name, product, quantity,
                        price, total, current_datetime, category, account_owner,
                        None, bank_account
                    ))

                    # Insert or update invoice in invoices table
                    cursor.execute("""
                        INSERT INTO invoices (invoice_number, created_at)
                        VALUES (%s, %s)
                        ON CONFLICT (invoice_number) DO NOTHING
                    """, (invoice_number, current_datetime))

                    # Calculate the total for this invoice (sum of all items)
                    cursor.execute("""
                        SELECT SUM(total) FROM sale WHERE invoice_no = %s
                    """, (invoice_number,))
                    invoice_total = cursor.fetchone()[0] or 0

                    # Check if this invoice already exists in sales_list
                    cursor.execute("""
                        SELECT COUNT(*) FROM sales_list WHERE invoice_no = %s
                    """, (invoice_number,))
                    exists = cursor.fetchone()[0] > 0

                    if exists:
                        # Update existing sales_list entry
                        cursor.execute("""
                            UPDATE sales_list 
                            SET invoice_amount = %s, 
                                balance = %s
                            WHERE invoice_no = %s
                        """, (invoice_total, invoice_total, invoice_number))
                    else:
                        # Insert new sales_list entry
                        cursor.execute("""
                            INSERT INTO sales_list (
                                customer_name, invoice_no, invoice_date, invoice_amount, 
                                paid_amount, balance, payment_status, category, account_owner, reference_no
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            customer_name, invoice_number, invoice_date, invoice_total,
                            0, invoice_total, 'Not Paid', category, account_owner, None
                        ))

                # Handle recurring products (Monthly, Quarterly, Annual)
                elif frequency in ['Monthly', 'Quarterly', 'Annual']:
                    cursor.execute("SELECT MAX(sales_acc_id) FROM sales_account;")
                    max_result = cursor.fetchone()
                    last_sales_acc_id = max_result[0] if max_result and max_result[0] is not None else 0
                    sales_acc_id = last_sales_acc_id + 1

                    cursor.execute("""
                        INSERT INTO sales_account (
                            sales_acc_id, invoice_date, invoice_number, customer_name, 
                            product, quantity, price, total, created_at, 
                            category, account_owner, frequency, status, bank_account
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING invoice_number
                    """, (
                        sales_acc_id, invoice_date, invoice_number, customer_name,
                        product, quantity, price, total, current_datetime,
                        category, account_owner, frequency, 'Active', bank_account
                    ))

                    result = cursor.fetchone()
                    if result is None:
                        raise Exception("Failed to create sales account entry")
                    sales_acc_invoice_no = result[0]

                    cursor.execute("""
                        INSERT INTO invoices (invoice_number, created_at)
                        VALUES (%s, %s)
                        ON CONFLICT (invoice_number) DO NOTHING
                    """, (sales_acc_invoice_no, current_datetime))
                    conn.commit()

                    today = datetime.today().date()

                    if frequency == 'Monthly':
                        delta = relativedelta(months=1)
                    elif frequency == 'Quarterly':
                        delta = relativedelta(months=3)
                    elif frequency == 'Annual':
                        delta = relativedelta(years=1)
                    else:
                        delta = None

                    if delta:
                        next_due_date = invoice_date.date()
                        while next_due_date <= today + delta:
                            new_invoice_number = generate_next_invoice_number()

                            cursor.execute("""
                                INSERT INTO sale (
                                    invoice_date, invoice_no, customer_name, product, quantity, 
                                    price, total, date_created, category, account_owner, 
                                    sales_acc_invoice_no, bank_account
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                next_due_date, new_invoice_number, customer_name, product, quantity,
                                price, total, current_datetime, category, account_owner,
                                sales_acc_invoice_no, bank_account
                            ))

                            cursor.execute("""
                                INSERT INTO invoices (invoice_number, created_at)
                                VALUES (%s, %s)
                                ON CONFLICT (invoice_number) DO NOTHING
                            """, (new_invoice_number, current_datetime))

                            # Calculate the total for this invoice (sum of all items)
                            cursor.execute("""
                                SELECT SUM(total) FROM sale WHERE invoice_no = %s
                            """, (new_invoice_number,))
                            invoice_total = cursor.fetchone()[0] or 0

                            cursor.execute("""
                                INSERT INTO sales_list (
                                    customer_name, invoice_no, invoice_date, invoice_amount, 
                                    paid_amount, balance, payment_status, category, account_owner, reference_no
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                customer_name, new_invoice_number, next_due_date, invoice_total,
                                0, invoice_total, 'Not Paid', category, account_owner, sales_acc_invoice_no
                            ))

                            conn.commit()
                            next_due_date += delta

                conn.commit()

                cursor.execute("""
                    SELECT product as description, quantity, price as unit_price, total
                    FROM sale WHERE invoice_no = %s ORDER BY sales_id
                """, (invoice_number,))
                items_result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                all_items = [dict(zip(columns, row)) for row in items_result] if items_result else []

                invoice_data = {
                    'customer_name': customer_name,
                    'invoice_number': invoice_number,
                    'invoice_date': invoice_date.strftime('%d-%m-%Y'),
                    'items': all_items,
                    'total_amount': sum(item['total'] for item in all_items),
                    'notes': notes,
                    'payment_status': 'Not Paid'
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
                    return jsonify({
                        'status': 'add_another',
                        'message': 'Sale added successfully! Add another item?',
                        'invoice_number': invoice_number,
                        'client_name': customer_name,
                        'invoice_date': invoice_date.strftime('%Y-%m-%d'),
                        'invoice_url': url_for('download_invoice', filename=filename),
                        'current_items': all_items
                    })
                else:
                    return jsonify(response)

            except Exception as e:
                if conn:
                    conn.rollback()
                app.logger.error(f"Error saving sale: {str(e)}")
                return jsonify({'status': 'error', 'message': f'An error occurred: {str(e)}'}), 500
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    product_names = read_product_names()
    next_invoice_number = generate_next_invoice_number()
    categories = read_categories()
    accounts = read_account_owners()
    client_names = read_client_names()
    bank_accounts = read_bank_accounts()

    customer_name = request.args.get('customer_name', '')
    invoice_number = request.args.get('invoice_number', next_invoice_number)
    date_created = datetime.today().strftime('%Y-%m-%d')

    return render_template('sales_entry.html',
                           product_names=product_names,
                           next_invoice_number=invoice_number,
                           customer_name=customer_name,
                           categories=categories,
                           accounts=accounts,
                           client_names=client_names,
                           bank_accounts=bank_accounts,
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
    categories = read_categories()
    account_owners = read_account_owners()

    # Set default date range
    today = datetime.today()
    default_start_date = (today - timedelta(days=730)).strftime('%Y-%m-%d')
    default_end_date = (today + timedelta(days=7)).strftime('%Y-%m-%d')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if request.method == 'POST':
            start_date = request.form.get('start_date') or default_start_date
            end_date = request.form.get('end_date') or default_end_date
            account_owner = request.form.get('account_owner')
            category = request.form.get('category')

            # Start building query
            query = """
                       SELECT sales_id, invoice_date, invoice_no, customer_name, account_owner,
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

            if account_owner:
                query += " AND account_owner = %s"
                params.append(account_owner)

            if category:
                query += " AND category = %s"
                params.append(category)

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
                               account_owners=account_owners,
                               categories=categories,
                               default_start_date=default_start_date,
                               default_end_date=default_end_date)

    return render_template('search_invoices.html',
                           invoices=invoices,
                           account_owners=account_owners,
                           categories=categories,
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

# Products route
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET' and ('term' in request.args or 'all' in request.args):
        search_term = request.args.get('term', '').strip()
        show_all = request.args.get('all', 'false').lower() == 'true'
        print(f"Search term received: {search_term}, Show all: {show_all}")

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Main query
            query = sql.SQL("""
                SELECT * FROM products WHERE status = 'Active'
            """)

            # Add WHERE clause only if not showing all and search term exists
            if not show_all and search_term:
                query = sql.SQL("""
                    {base_query}
                    WHERE product ILIKE %s OR isbn ILIKE %s
                """).format(base_query=query)
                params = (f'%{search_term}%', f'%{search_term}%')
            else:
                params = ()

            # Add ordering and limit
            query = sql.SQL("""
                {base_query}
                ORDER BY product
                LIMIT 100
            """).format(base_query=query)

            cur.execute(query, params)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            results = []
            for idx, row in enumerate(rows):
                print(f"Row {idx}: {row}")
                # Safely handle date_created formatting
                date_created = ''
                try:
                    date_created = row[7].strftime('%Y-%m-%d') if hasattr(row[7], 'strftime') else str(row[7])
                except Exception as e:
                    print(f"Date formatting error: {e}")
                    date_created = str(row[7])

                results.append({
                    'label': f"{row[1]}",
                    'value': row[1],  # product name
                    'data': {
                        'product_number': row[0],
                        'product': row[1],
                        'edition': row[2],
                        'isbn': row[3],
                        'date_published': row[4],
                        'publisher': row[5],
                        'author': row[6],
                        'date_created': date_created,
                        'frequency': row[8],
                    }
                })
            return jsonify(results)
        except Exception as e:
            print(f"Database error: {e}")
            return jsonify([])

    elif request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'delete':
            try:
                product_number = request.form['product_number']
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                            UPDATE products SET status = 'Inactive' WHERE product_number = %s
                        """, (product_number,))
                conn.commit()
                return jsonify({'success': True, 'message': 'Product deleted successfully'})
            except Exception as e:
                print(f"Error deleting product: {e}")
                return jsonify({'success': False, 'message': 'Failed to delete product'}), 400
            finally:
                cur.close()
                conn.close()
        if form_type == 'edit':
            try:
                # Get all form data
                product_number = request.form['product_number']
                product = request.form['product']
                edition = request.form['edition']
                isbn = request.form['isbn']
                date_published = request.form['date_published']
                publisher = request.form['publisher']
                author = request.form['author']
                date_created = request.form['date_created']
                frequency = request.form['frequency']
                conn = get_db_connection()
                cur = conn.cursor()

                # Update query
                update_query = sql.SQL("""
                        UPDATE products
                        SET 
                            product = %s,
                            edition = %s,
                            isbn = %s,
                            date_published = %s,
                            publisher = %s,
                            author = %s,
                            date_created = %s,
                            frequency = %s
                        WHERE product_number = %s
                        RETURNING *
                    """)

                cur.execute(update_query, (
                    product,
                    edition,
                    isbn,
                    date_published,
                    publisher,
                    author,
                    date_created,
                    frequency,
                    product_number
                ))

                # Get the updated record
                updated_record = cur.fetchone()
                conn.commit()
                # Format the updated record for response

                date_created = ''
                try:
                    date_created = updated_record[7].strftime('%Y-%m-%d') if hasattr(updated_record[7],
                                                                          'strftime') else str(
                        updated_record[7])
                except Exception as e:
                    print(f"Date formatting error: {e}")
                    date_created = str(updated_record[7])

                updated_data = {
                    'product_number':updated_record[0],
                    'product': updated_record[1],
                    'edition': updated_record[2],
                    'isbn': updated_record[3],
                    'date_published': updated_record[4],
                    'publisher': updated_record[5],
                    'author': updated_record[6],
                    'date_created': date_created,
                    'frequency': updated_record[8],
                }

                return jsonify({

                    'success': True,
                    'message': 'Product updated successfully',
                    'updated_data': updated_data
                })
            except Exception as e:
                print(f"Error updating product: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Failed to update product: {str(e)}'
                }), 400
            finally:
                cur.close()
                conn.close()

        elif form_type == 'add':
            try:
                # Get form fields with proper default values
                product = request.form.get('product', '').strip()
                edition = request.form.get('edition', '').strip()
                isbn = request.form.get('isbn', '').strip()
                date_published = request.form.get('date_published', '').strip()
                publisher = request.form.get('publisher', '').strip()
                author = request.form.get('author', '').strip()
                date_created = request.form.get('date_created', '').strip()
                frequency = request.form.get('frequency', '').strip()

                if not product:
                    return jsonify({'success': False, 'message': 'Product name is required'}), 400
                if not isbn:
                    return jsonify({'success': False, 'message': 'ISBN is required'}), 400
                if not date_published:
                    return jsonify({'success': False, 'message': 'Date Published is required'}), 400

                conn = get_db_connection()
                cur = conn.cursor()

                insert_query = """
                            INSERT INTO products (
                                product, edition, isbn, date_published, publisher, 
                                author, date_created, frequency, status
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Active')
                            RETURNING product, date_created
                        """

                cur.execute(insert_query, (
                    product, edition, isbn, date_published,
                    publisher, author, date_created, frequency
                ))

                # Safely handle the returned data
                result = cur.fetchone()
                if not result:
                    raise Exception("No data returned after insert")

                product, date_created = result
                conn.commit()

                # Format the date safely
                formatted_date = ''
                try:
                    formatted_date = date_created.strftime('%Y-%m-%d') if hasattr(date_created, 'strftime') else str(
                        date_created)
                except Exception as e:
                    print(f"Date formatting error: {e}")
                    formatted_date = str(date_created)

                return jsonify({
                    'success': True,
                    'message': 'Product added successfully',
                    'product': product,
                    'date_created': formatted_date
                })

            except Exception as e:
                print(f"Error adding product: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Failed to add product: {str(e)}'
                }), 400
            finally:
                if 'cur' in locals(): cur.close()
                if 'conn' in locals(): conn.close()

        return jsonify({'success': False, 'message': 'Invalid form type'}), 400

    return render_template('products/search_product.html')

# Edit product Route
@app.route('/edit_product')
def edit_product():
    return render_template('products/edit-product.html')

# Add Product Route
@app.route('/add_product')
def add_product():
    return render_template('products/add-product.html')

# Stores Route
@app.route('/stores')
def stores_menu():
    return render_template('stores_menu.html')

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
                WHERE status != 'Not Active'
            """)

            # Add WHERE clause only if not showing all and search term exists
            if not show_all and search_term:
                query = sql.SQL("""
                    {base_query}
                    WHERE status != 'Not Active' AND (account_name ILIKE %s OR service_provider ILIKE %s)
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
                invoice_number = request.form['invoice_number']  # Get the invoice number from the form
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

                conn = get_db_connection()
                cur = conn.cursor()
                # Insert into billing_account table
                insert_billing_query = sql.SQL("""
                           INSERT INTO billing_account (
                               service_provider, account_name, account_number, category, paybill_number, 
                               ussd_number, frequency, billing_date, bill_amount, account_owner, 
                               status, bank_account, invoice_number
                           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           RETURNING created_date
                       """)
                cur.execute(insert_billing_query, (
                    service_provider, account_name, account_number, category, paybill_number,
                    ussd_number, frequency, billing_date, bill_amount, account_owner,
                    status, bank_account, invoice_number
                ))
                created_date = cur.fetchone()[0]

                # Insert into invoices table
                insert_invoice_query = sql.SQL("""
                           INSERT INTO invoices (
                               invoice_number
                           ) VALUES (%s)
                       """)
                cur.execute(insert_invoice_query, (
                    invoice_number))
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


@app.route('/delete_billing_account', methods=['POST'])
def delete_billing_account():
    try:
        invoice_number = request.form.get('invoice_number')
        if not invoice_number:
            return jsonify({
                'success': False,
                'message': 'Invoice number is required'
            }), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Update the status to 'Not active'
        update_query = sql.SQL("""
            UPDATE billing_account
            SET status = 'Not Active'
            WHERE invoice_number = %s
            RETURNING invoice_number, account_name
        """)

        cur.execute(update_query, (invoice_number,))
        result = cur.fetchone()
        conn.commit()

        if result:
            return jsonify({
                'success': True,
                'message': f"Billing Account '{result[1]}' (with invoice number: {result[0]}) has been deleted",
                'invoice_number': result[0]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No account found with that invoice number'
            }), 404

    except Exception as e:
        print(f"Error deleting the account: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to delete account: {str(e)}'
        }), 500
    finally:
        cur.close()
        conn.close()


def generate_next_invoice_number():
    conn = get_db_connection()
    cur = conn.cursor()

    now = datetime.now()
    month = f"{now.month:02d}"
    year_short = f"{now.year % 100:02d}"

    cur.execute(
        sql.SQL("SELECT invoice_number FROM invoices WHERE invoice_number LIKE %s ORDER BY id DESC LIMIT 1"),
        [f"TKB/{month}%/{year_short}"]
    )
    last_invoice = cur.fetchone()

    if last_invoice:
        last_seq = int(last_invoice[0].split("/")[1][2:])
        next_seq = last_seq + 1
    else:
        next_seq = 1

    invoice_number = f"TKB/{month}{next_seq:03d}/{year_short}"
    cur.close()
    conn.close()
    return invoice_number


@app.route('/get_next_invoice_number')
def get_next_invoice_number():
    invoice_number = generate_next_invoice_number()
    return {'invoice_number': invoice_number}


@app.route('/search-bill')
def search_bill():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch only account_owner names from database
    cur.execute("SELECT DISTINCT account_owner FROM account_owner ORDER BY account_owner")
    owners = [row[0] for row in cur.fetchall()]  # Extract just the names

    conn.close()

    return render_template('bills/search-bills.html', owners=owners)


def parse_date(date_str):
    """Parse date from multiple possible formats"""
    for fmt in ('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Date '{date_str}' doesn't match any expected format")


@app.route('/search-bills', methods=['POST'])
def search_bills():
    try:
        data = request.get_json()

        # Parse dates with improved error handling
        # Parse dates with improved error handling
        try:
            start_date = parse_date(data['start_date']).strftime('%Y-%m-%d')
            end_date = parse_date(data['end_date']).strftime('%Y-%m-%d')
        except ValueError as e:
            return jsonify({
                'error': f"Invalid date format: {str(e)}. Supported formats: DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY, DD/MM/YY"
            }), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Base query
        query = """
            SELECT 
                account_name,
                account_number,
                billing_date,
                bill_amount
            FROM bills 
            WHERE billing_date BETWEEN %s AND %s
            AND status != 'Not Active'
            AND pay_status != 'Paid'

        """
        params = [start_date, end_date]

        # Add filters if specified
        if data.get('category') and data['category']:
            query += " AND category = %s"
            params.append(data['category'])

        if data.get('account_owner') and data['account_owner']:
            query += " AND account_owner = %s"
            params.append(data['account_owner'])

        query += " ORDER BY billing_date DESC"

        cur.execute(query, params)

        # Properly convert rows to dictionaries
        columns = [desc[0] for desc in cur.description]
        bills = []
        for row in cur.fetchall():
            bill = dict(zip(columns, row))
            # Format date for display
            if 'billing_date' in bill and bill['billing_date']:
                bill_date = datetime.strptime(str(bill['billing_date']), '%Y-%m-%d')
                bill['billing_date'] = bill_date.strftime('%d/%m/%y')
            bills.append(bill)

        return jsonify(bills)

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RECEIPT_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
