import psycopg2
import openpyxl
from datetime import datetime

def convert_date(date_str):
    """Convert DD/MM/YYYY to YYYY-MM-DD format"""
    try:
        if isinstance(date_str, str):
            return datetime.strptime(date_str, "%d/%m/%Y").date()
        return date_str  # Return as-is if already a date object
    except Exception as e:
        print(f"Warning: Could not parse date {date_str} - using None")
        return None

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="34.56.172.17",
    database="invoice-demo",
    user="postgres",
    password="Speedthecollapse2025"
)
cur = conn.cursor()

# Load the Excel file
workbook = openpyxl.load_workbook("billing-accounts.xlsx") #change file name

# Select the appropriate worksheet
worksheet = workbook["Sheet2"]  #change sheet name

# Clear the table before inserting new data
#cur.execute("TRUNCATE TABLE Eng_Dictionary;")

# Iterate over the rows in the worksheet
for row in worksheet.iter_rows(min_row=2, values_only=True):
    # Extract the values from each cell in the row
    values = [str(cell).strip() if cell is not None else "" for cell in row]

    try:
        # Convert date fields (assuming positions 7 and 10 are dates)
        billing_date = convert_date(values[6])
        created_date = convert_date(values[9])

        query = """
            INSERT INTO bills (
                service_provider, account_name, account_number, 
                category, paybill_number, ussd_number, billing_date, bill_amount, 
                account_owner, created_date, pay_status, bill_invoice_number, invoice_number, 
                status, bank_account
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        cur.execute(query, (
            values[0],  # service_provider
            values[1],  # account_name
            values[2],  # account_number
            values[3],  # category
            values[4],  # paybill_number
            values[5],  # ussd_number
            billing_date,
            values[7],  # bill_amount
            values[8],  # account_owner
            created_date,
            values[10],
            values[11],  # bill_invoice_number
            values[12],  # invoice_number
            values[13],  # status
            values[14]  # bank_account
        ))
    except Exception as e:
        print(f"Error inserting row: {values}")
        print(f"Error details: {e}")
        conn.rollback()

# Commit the changes and close the database connection
conn.commit()
cur.close()
conn.close()

#Showing its completed
print("Done!")
