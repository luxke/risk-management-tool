from flask import Blueprint, render_template, request
from db import get_db_connection
from services.auth_service import login_required

risks_bp = Blueprint("risks", __name__)


@risks_bp.route('/add-risk', methods=['GET', 'POST'])
@login_required
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
        """, (
            Tittle,
            description,
            probability,
            impact,
            score
        ))

        conn.commit()
        conn.close()


    return render_template("add_risk.html")