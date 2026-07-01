import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Luxke@SQL2026",
        database="institution_db"
    )
    return connection



























































