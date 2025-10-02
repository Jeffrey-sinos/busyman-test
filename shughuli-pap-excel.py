import os
from dotenv import load_dotenv
import psycopg2
import openpyxl

load_dotenv()


def get_db_connection():
    print("Connecting to DB...")
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    print("Connected!")
    return conn


conn = get_db_connection()
cur = conn.cursor()
print(">>> Script started <<<")

# Load the Excel file
workbook = openpyxl.load_workbook("aaab-data.xlsx")

# Select the appropriate worksheet
worksheet = workbook["Bills"]

# Clear the table before inserting new data

cur.execute("TRUNCATE TABLE aaab_bills CASCADE;")

# Read last checkpoint (default to row 2 if no progress file)
try:
    with open("bills.txt", "r") as f:
        start_row = int(f.read().strip()) + 1
except FileNotFoundError:
    start_row = 2

print(f"Resuming from Excel row {start_row}")

# Iterate over rows starting from the checkpoint
for excel_row_num, row in enumerate(worksheet.iter_rows(min_row=start_row, values_only=True), start=start_row):
    values = [None if (cell is None or cell == "") else cell for cell in row]

    if len(values) >= 16:
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
                values[12],
                values[13],
                values[14],
                values[15],

            ]

            query = """
                INSERT INTO aaab_bills 
                (service_provider, ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, insert_values)
            conn.commit()

            # Save checkpoint
            with open("receipts.txt", "w") as f:
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
