from flask import Blueprint, render_template
from db import get_db_connection
from services.auth_service import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route('/')
@login_required
def dashboard():


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM risks")
    total_risks = cursor.fetchone()['total']

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