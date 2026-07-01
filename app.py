from flask import Flask, render_template 
from db import get_db_connection 

app = Flask(__name__)
@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM risks")
    total_risks = cursor.fetchone()[0]
    conn.close()

    return render_template("dashboard.html", total_risks=total_risks)

if __name__ == '__main__':
    app.run(debug=True)




    
