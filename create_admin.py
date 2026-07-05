from werkzeug.security import generate_password_hash
from db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

hashed_password = generate_password_hash("admin123")

cursor.execute("""
INSERT INTO users (full_name, email, Password, role)
VALUES (%s, %s, %s, %s)
""", (
    "System Administrator",
    "admin@gmail.com",
    hashed_password,
    "Admin"
))

conn.commit()

print("Admin account created successfully!")

conn.close()