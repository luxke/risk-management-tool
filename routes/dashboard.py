from flask import Blueprint, render_template, session
from db import get_db_connection
from services.auth_service import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ==========================================
    # ADMIN DASHBOARD
    # ==========================================
    if session["role"] == "Admin":

        # Total Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
        """)
        total_risks = cursor.fetchone()["total"]

        # High Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Score >= 15
        """)
        high_risks = cursor.fetchone()["total"]

        # Medium Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Score BETWEEN 8 AND 14
        """)
        medium_risks = cursor.fetchone()["total"]

        # Low Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Score <= 7
        """)
        low_risks = cursor.fetchone()["total"]

        # All Risks
        cursor.execute("""
            SELECT
                r.Risk_id,
                r.Tittle,
                r.Description,
                r.Probability,
                r.Impact,
                r.Score,
                r.status,
                u.full_name,
                d.department_name
            FROM risks r
            LEFT JOIN users u
                ON r.Owner_id = u.user_id
            LEFT JOIN departments d
                ON r.department_id = d.department_id
            ORDER BY r.Risk_id DESC
        """)

    # ==========================================
    # RISK MANAGER DASHBOARD
    # ==========================================
    elif session["role"] == "Risk Manager":

        # Total Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE department_id=%s
        """, (session["department_id"],))
        total_risks = cursor.fetchone()["total"]

        # High Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE department_id=%s
            AND Score >=15
        """, (session["department_id"],))
        high_risks = cursor.fetchone()["total"]

        # Medium Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE department_id=%s
            AND Score BETWEEN 8 AND 14
        """, (session["department_id"],))
        medium_risks = cursor.fetchone()["total"]

        # Low Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE department_id=%s
            AND Score <=7
        """, (session["department_id"],))
        low_risks = cursor.fetchone()["total"]

        # Department Risks
        cursor.execute("""
            SELECT
                r.Risk_id,
                r.Tittle,
                r.Description,
                r.Probability,
                r.Impact,
                r.Score,
                r.status,
                u.full_name
            FROM risks r
            LEFT JOIN users u
                ON r.Owner_id = u.user_id
            WHERE r.department_id=%s
            ORDER BY r.Risk_id DESC
        """, (session["department_id"],))

    # ==========================================
    # EMPLOYEE DASHBOARD
    # ==========================================
    else:

        # Total Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Owner_id=%s
        """, (session["user_id"],))
        total_risks = cursor.fetchone()["total"]

        # High Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Owner_id=%s
            AND Score >=15
        """, (session["user_id"],))
        high_risks = cursor.fetchone()["total"]

        # Medium Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Owner_id=%s
            AND Score BETWEEN 8 AND 14
        """, (session["user_id"],))
        medium_risks = cursor.fetchone()["total"]

        # Low Risks
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Owner_id=%s
            AND Score <=7
        """, (session["user_id"],))
        low_risks = cursor.fetchone()["total"]

        # My Risks
        cursor.execute("""
            SELECT
                Risk_id,
                Tittle,
                Description,
                Probability,
                Impact,
                Score,
                status
            FROM risks
            WHERE Owner_id=%s
            ORDER BY Risk_id DESC
        """, (session["user_id"],))

    risks = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_risks=total_risks,
        high_risks=high_risks,
        medium_risks=medium_risks,
        low_risks=low_risks,
        risks=risks
    )