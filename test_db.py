from db import get_db_connection

try:
    conn = get_db_connection()
    print("connected to MYSQL successfully")
    conn.close()
except Exception as e:
    print("connection failed:", e)






































