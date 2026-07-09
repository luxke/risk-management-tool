from flask import Blueprint, render_template, request,session
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

        owner_id = session["user_id"]
        department_id = session["department_id"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
        """
            INSERT INTO risks
            (Tittle,
             Description,
             Probability,
             Impact,
             Score,
             Owner_id,
             department_id)
             VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            Tittle,
            description,
            probability,
            impact,
            score,
            owner_id,
            department_id
        ))

        conn.commit()
        conn.close()


    return render_template("add_risk.html")