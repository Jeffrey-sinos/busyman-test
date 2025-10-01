import os
from dotenv import load_dotenv
import psycopg2
import openpyxl

load_dotenv()


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )


conn = get_db_connection()
cur = conn.cursor()

# Load the Excel file
workbook = openpyxl.load_workbook("aaab-data.xlsx")

# Select the appropriate worksheet
worksheet = workbook["SalesList"]

# Clear the table before inserting new data

cur.execute("TRUNCATE TABLE aaab_sales_list CASCADE;")

# Read last checkpoint (default to row 2 if no progress file)
try:
    with open("sales_list.txt", "r") as f:
        start_row = int(f.read().strip()) + 1
except FileNotFoundError:
    start_row = 2

print(f"Resuming from Excel row {start_row}")

# Iterate over rows starting from the checkpoint
for excel_row_num, row in enumerate(worksheet.iter_rows(min_row=start_row, values_only=True), start=start_row):
    values = [None if (cell is None or cell == "") else cell for cell in row]

    if len(values) >= 12:
        try:
            insert_values = [
                values[1],
                values[2],
                values[3],
                values[4],
                values[5],
                values[6],
                values[7],
                values[8],
                values[9],
                values[10],
                values[11],
            ]

            query = """
                INSERT INTO aaab_sales_list 
                (customer_name, invoice_no, invoice_date, invoice_amount, paid_amount, balance, payment_status, notes, category, account_owner, reference_no) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, insert_values)
            conn.commit()

            # Save checkpoint
            with open("sales_list.txt", "w") as f:
                f.write(str(excel_row_num))

            print(f"Inserted row {excel_row_num}")

        except Exception as e:
            conn.rollback()
            print(f"Error on row {excel_row_num}: {e}")
            print(f"Row data: {values}")
    else:
        print(f"Skipping row {excel_row_num}: Not enough values ({len(values)})")

cur.close()
conn.close()
print("Done!")
