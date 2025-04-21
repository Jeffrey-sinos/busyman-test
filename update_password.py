from werkzeug.security import generate_password_hash
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
)
cur = conn.cursor()

# Fetch users with passwords
cur.execute("SELECT user_id, password FROM users")
users = cur.fetchall()

# Loop through users and update plain text passwords
for user_id, password in users:
    # Check if the password is already hashed (supports both pbkdf2 and scrypt)
    if not (password.startswith('pbkdf2:sha256:') or password.startswith('scrypt:')):
        hashed_password = generate_password_hash(password)
        cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (hashed_password, user_id))

conn.commit()
cur.close()
conn.close()

print("Passwords updated successfully!")
