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

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
        """)
        total_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Score >= 15
        """)
        high_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Score BETWEEN 8 AND 14
        """)
        medium_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Score <= 7
        """)
        low_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT
                r.Risk_id,
                r.Tittle,
                r.Description,
                r.Owner_id,
                r.category_id,
                r.department_id,
                r.Probability,
                r.Impact,
                r.Score,

                rs.status_name,

                u.full_name,
                d.department_name

            FROM risks r

            LEFT JOIN risk_status rs
                ON r.status_id = rs.status_id

            LEFT JOIN users u
                ON r.Owner_id = u.user_id

            LEFT JOIN departments d
                ON r.department_id = d.department_id

            ORDER BY r.Risk_id DESC
        """)

        risks = cursor.fetchall()

    # ==========================================
    # RISK MANAGER DASHBOARD
    # ==========================================
    elif session["role"] == "Risk Manager":

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE department_id=%s
        """, (session["department_id"],))
        total_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE department_id=%s
            AND Score >=15
        """, (session["department_id"],))
        high_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE department_id=%s
            AND Score BETWEEN 8 AND 14
        """, (session["department_id"],))
        medium_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE department_id=%s
            AND Score <=7
        """, (session["department_id"],))
        low_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT
                r.Risk_id,
                r.Tittle,
                r.Description,
                r.Owner_id,
                r.department_id,
                r.Probability,
                r.Impact,
                r.Score,

                rs.status_name,

                u.full_name

            FROM risks r

            LEFT JOIN risk_status rs
                ON r.status_id = rs.status_id

            LEFT JOIN users u
                ON r.Owner_id = u.user_id

            WHERE r.department_id=%s

            ORDER BY r.Risk_id DESC
        """, (session["department_id"],))

        risks = cursor.fetchall()

    # ==========================================
    # EMPLOYEE DASHBOARD
    # ==========================================
    else:

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Owner_id=%s
        """, (session["user_id"],))
        total_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Owner_id=%s
            AND Score >=15
        """, (session["user_id"],))
        high_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Owner_id=%s
            AND Score BETWEEN 8 AND 14
        """, (session["user_id"],))
        medium_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM risks
            WHERE Owner_id=%s
            AND Score <=7
        """, (session["user_id"],))
        low_risks = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT
                r.Risk_id,
                r.Tittle,
                r.Description,
                r.department_id,
                r.Probability,
                r.Impact,
                r.Score,

                rs.status_name

            FROM risks r

            LEFT JOIN risk_status rs
                ON r.status_id = rs.status_id

            WHERE r.Owner_id=%s

            ORDER BY r.Risk_id DESC
        """, (session["user_id"],))

        risks = cursor.fetchall()
    # ==========================================
    # STATUS CHART DATA
    # ==========================================

    if session["role"] == "Admin":

        cursor.execute("""
            SELECT
                rs.status_name,
                COUNT(r.Risk_id) AS total
            FROM risk_status rs
            LEFT JOIN risks r
                ON rs.status_id = r.status_id
            GROUP BY rs.status_id
            ORDER BY rs.status_id
        """)

    elif session["role"] == "Risk Manager":

        cursor.execute("""
            SELECT
                rs.status_name,
                COUNT(r.Risk_id) AS total
            FROM risk_status rs
            LEFT JOIN risks r
                ON rs.status_id = r.status_id
                AND r.department_id=%s
            GROUP BY rs.status_id
            ORDER BY rs.status_id
        """, (session["department_id"],))

    else:

        cursor.execute("""
            SELECT
                rs.status_name,
                COUNT(r.Risk_id) AS total
            FROM risk_status rs
            LEFT JOIN risks r
                ON rs.status_id = r.status_id
                AND r.Owner_id=%s
            GROUP BY rs.status_id
            ORDER BY rs.status_id
        """, (session["user_id"],))

    status_chart = cursor.fetchall()

    
    # ==========================================
    # DEPARTMENT CHART
    # ==========================================

    if session["role"] == "Admin":

        cursor.execute("""
            SELECT
                d.department_name,
                COUNT(r.Risk_id) total
            FROM departments d
            LEFT JOIN risks r
                ON d.department_id=r.department_id
            GROUP BY d.department_id
            ORDER BY total DESC
        """)

    else:

        cursor.execute("""
            SELECT
                d.department_name,
                COUNT(r.Risk_id) total
            FROM departments d
            LEFT JOIN risks r
                ON d.department_id=r.department_id
            WHERE d.department_id=%s
            GROUP BY d.department_id
        """, (session["department_id"],))

    department_chart = cursor.fetchall()


    # ==========================================
    # CATEGORY CHART
    # ==========================================

    if session["role"] == "Admin":

        cursor.execute("""
            SELECT
                c.category_name,
                COUNT(r.Risk_id) total
            FROM risk_categories c
            LEFT JOIN risks r
                ON c.category_id=r.category_id
            GROUP BY c.category_id
            ORDER BY total DESC
        """)

    elif session["role"] == "Risk Manager":

        cursor.execute("""
            SELECT
                c.category_name,
                COUNT(r.Risk_id) total
            FROM risk_categories c
            LEFT JOIN risks r
                ON c.category_id=r.category_id
            WHERE r.department_id=%s
            GROUP BY c.category_id
        """, (session["department_id"],))

    else:

        cursor.execute("""
            SELECT
                c.category_name,
                COUNT(r.Risk_id) total
            FROM risk_categories c
            LEFT JOIN risks r
                ON c.category_id=r.category_id
            WHERE r.Owner_id=%s
            GROUP BY c.category_id
        """, (session["user_id"],))

    category_chart = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",

        total_risks=total_risks,
        high_risks=high_risks,
        medium_risks=medium_risks,
        low_risks=low_risks,

        risks=risks,

        status_chart=status_chart,
        department_chart=department_chart,
        category_chart=category_chart
    )





























