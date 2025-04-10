# import appropriate libraries
from flask import Flask,flash, session, render_template, request, redirect, url_for, send_from_directory, jsonify, make_response
import os
import io
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
from psycopg2 import sql
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash # password hashing
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Direct flask to templates folder
app = Flask(__name__, template_folder='../templates')
app.secret_key = 'your_secret_key'

# Create invoice folder to store downloaded invoices
app.config['UPLOAD_FOLDER'] = 'invoices'
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

# display products function
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

# display categories function
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

# display account owners function
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

# display clients function
def read_client_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT customer_name FROM sales ORDER BY customer_name;")
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
def generate_receipt(sales_id, customer_name, invoice_no, amount_paid,
                   previous_bal, new_bal, payment_date, is_full_payment):

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Receipt Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "PAYMENT RECEIPT")
        p.line(100, 745, 500, 745)


        # Receipt Details
        p.setFont("Helvetica", 12)
        y_position = 700
        details = [
            f"Receipt No: RCPT-{sales_id:05d}",
            f"Invoice No: {invoice_no}",
            f"Customer: {customer_name}",
            f"Payment Date: {payment_date.strftime('%Y-%m-%d')}",
            "",
            f"Amount Paid: ${amount_paid:.2f}",
            f"Previous Balance: ${previous_bal:.2f}",
            f"New Balance: ${new_bal:.2f}",
            "",
            f"Payment Status: {'FULL PAYMENT' if is_full_payment else 'PARTIAL PAYMENT'}"
        ]

        for line in details:
            p.drawString(100, y_position, line)
            y_position -= 30

        # Payment summary box
        p.rect(100, y_position - 50, 400, 80)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(120, y_position - 20, "PAYMENT SUMMARY")
        p.setFont("Helvetica", 12)
        p.drawString(120, y_position - 50, f"Total Paid: ${amount_paid:.2f}")
        p.drawString(120, y_position - 80, f"Remaining Balance: ${new_bal:.2f}")

        p.showPage()
        p.save()

        buffer.seek(0)
        return buffer
# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'] # Get the name from the form
        password = request.form['password'] # Get the password from the form

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT user_id, role, username, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        cur.close()
        conn.close()

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

#Sales Menu route
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
                invoice_date = request.form.get('invoice_date')
                invoice_number = request.form.get('invoice_number')
                customer_name = request.form.get('client_name')
                product = request.form.get('product')
                quantity = int(request.form.get('quantity'))
                price = float(request.form.get('price'))
                category = request.form.get('category')
                account_owner = request.form.get('account')
                notes = request.form.get('notes', '')
                transaction_type = request.form.get('transaction_type')
                add_another = request.form.get('add_another', 'no') == 'yes'

                # Calculation of Values
                total = round(quantity * price, 2)
                paid = 0
                balance = total
                paid_date = None
                acc_status = 'Active'
                payment_status = 'Not Paid'

                if quantity < 0:
                    total = abs(total)
                    payment_status = 'Refund'

                current_datetime = get_current_datetime()

                # Save to database
                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO sales (
                        invoice_date, invoice_no, customer_name, product, qty, 
                        amt, total, paid, bal, paid_date, category, 
                        account_owner, acc_status, payment_status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
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
                    'invoice_date': invoice_date,
                    'items': [{
                        'description': item['description'],
                        'quantity': item['quantity'],
                        'unit_price': item['unit_price'],
                        'total': item['total']
                    }for item in all_items],
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

    return render_template('sales_entry.html',
                           product_names=product_names,
                           next_invoice_number=invoice_number,
                           customer_name=customer_name,
                           categories=categories,
                           accounts=accounts,
                           client_names=client_names,
                           current_date=get_current_date())

# Download invoice route
@app.route('/invoices/<filename>')
def download_invoice(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

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

    # Verify permissions and fetch invoice
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

            receipt_buffer = generate_receipt(
                sales_id = sales_id,
                customer_name=customer_name,
                invoice_no = invoice_no,
                amount_paid = paid,
                previous_bal = float(invoice[11]),
                new_bal = balance,
                payment_date = datetime.now().date(),
                is_full_payment=(balance==0)
            )

            flash("Payment updated successfully!", "success")

            response = make_response(receipt_buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=receipt_{invoice_no}.pdf'

            return response

            return redirect(url_for('view_sales', sales_id = sales_id))
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

# View users route
@app.route('/view_users')
def view_users():
    if 'user_id' not in session or session.get('role') != 1:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, role FROM users ORDER BY user_id ASC")
    users = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('view_users.html', users=users)

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

    #Create canvas
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
            f"KSh {item['unit_price']:,.1f}",
            f"KSh {item['total']:,.1f}"
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

# Allow external hosting
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)