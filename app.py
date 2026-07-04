from flask import Flask, render_template
from db import get_db_connection

app = Flask(__name__)

@app.route('/')
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total risks
    cursor.execute("SELECT COUNT(*) AS total FROM risks")
    total_risks = cursor.fetchone()['total']

    # Get all risks
    cursor.execute("""
        SELECT
            Risk_id,
            Tittle,
            Probability,
            Impact,
            Score,
            status
        FROM risks
    """)

    risks = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_risks=total_risks,
        risks=risks
    )


from flask import request, redirect

@app.route('/add-risk', methods=['GET', 'POST'])
def add_risk():

    if request.method == 'POST':

        Tittle = request.form['Tittle']
        description = request.form['description']
        probability = request.form['probability']
        impact = request.form['impact']

        score = int(probability) * int(impact)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO risks
            (Tittle, Description, Probability, Impact, Score)
            VALUES (%s,%s,%s,%s,%s)
        """, (Tittle, description, probability, impact, score))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("add_risk.html")

if __name__ == '__main__':
    app.run(debug=True)
    
