from flask import Blueprint, render_template, request, session
from db import get_db_connection
from services.auth_service import login_required

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
@login_required
def reports():

    # Only Admin and Risk Managers
    if session["role"] not in ["Admin", "Risk Manager"]:
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ==========================================
    # REPORT FILTERS
    # ==========================================

    selected_department = request.args.get("department")
    selected_category = request.args.get("category")
    selected_status = request.args.get("status")

    # ==========================================
    # LOAD FILTER DROPDOWNS
    # ==========================================

    cursor.execute("""
        SELECT
            department_id,
            department_name
        FROM departments
        ORDER BY department_name
    """)
    all_departments = cursor.fetchall()

    cursor.execute("""
        SELECT
            category_id,
            category_name
        FROM risk_categories
        ORDER BY category_name
    """)
    all_categories = cursor.fetchall()

    cursor.execute("""
        SELECT
            status_id,
            status_name
        FROM risk_status
        ORDER BY status_id
    """)
    all_statuses = cursor.fetchall()

      # ==========================================
    # BUILD REPORT FILTER
    # ==========================================

    conditions = []
    params = []

    # Risk Manager only sees own department
    if session["role"] == "Risk Manager":
        conditions.append("department_id=%s")
        params.append(session["department_id"])

    # Admin Department Filter
    if session["role"] == "Admin" and selected_department:
        conditions.append("department_id=%s")
        params.append(selected_department)

    # Category Filter
    if selected_category:
        conditions.append("category_id=%s")
        params.append(selected_category)

    # Status Filter
    if selected_status:
        conditions.append("status_id=%s")
        params.append(selected_status)

    # Final WHERE clause
    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    params = tuple(params)

    # ==========================================
    # TOTAL RISKS
    # ==========================================

    cursor.execute(f"""
        SELECT COUNT(*) AS total
        FROM risks
        {where_clause}
    """, params)

    total = cursor.fetchone()["total"]

      # ==========================================
    # HIGH RISKS
    # ==========================================

    high_where = where_clause

    if high_where:
        high_where += " AND Score >= 15"
    else:
        high_where = "WHERE Score >= 15"

    cursor.execute(f"""
        SELECT COUNT(*) AS total
        FROM risks
        {high_where}
    """, params)

    high = cursor.fetchone()["total"]

    # ==========================================
    # MEDIUM RISKS
    # ==========================================

    medium_where = where_clause

    if medium_where:
        medium_where += " AND Score BETWEEN 8 AND 14"
    else:
        medium_where = "WHERE Score BETWEEN 8 AND 14"

    cursor.execute(f"""
        SELECT COUNT(*) AS total
        FROM risks
        {medium_where}
    """, params)

    medium = cursor.fetchone()["total"]

    # ==========================================
    # LOW RISKS
    # ==========================================

    low_where = where_clause

    if low_where:
        low_where += " AND Score <= 7"
    else:
        low_where = "WHERE Score <= 7"

    cursor.execute(f"""
        SELECT COUNT(*) AS total
        FROM risks
        {low_where}
    """, params)

    low = cursor.fetchone()["total"]

    # ==========================================
    # STATUS COUNTS
    # ==========================================

    status_counts = {}

    statuses = [
        (1, "open_risks"),
        (2, "assigned"),
        (3, "under_review"),
        (5, "monitoring"),
        (6, "closed")
    ]

    for status_id, key in statuses:

        if session["role"] == "Admin":

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM risks
                WHERE status_id=%s
            """, (status_id,))

        else:

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM risks
                WHERE department_id=%s
                AND status_id=%s
            """, (session["department_id"], status_id))

        status_counts[key] = cursor.fetchone()["total"]

    # ==========================================
    # DEPARTMENT REPORT
    # ==========================================

    if session["role"] == "Admin":

        cursor.execute("""
            SELECT
                d.department_name,
                COUNT(r.Risk_id) AS total_risks,
                SUM(
                    CASE
                        WHEN r.Score >= 15 THEN 1
                        ELSE 0
                    END
                ) AS high_risks
            FROM departments d
            LEFT JOIN risks r
                ON d.department_id = r.department_id
            GROUP BY d.department_id
            ORDER BY total_risks DESC
        """)

    else:

        cursor.execute("""
            SELECT
                d.department_name,
                COUNT(r.Risk_id) AS total_risks,
                SUM(
                    CASE
                        WHEN r.Score >= 15 THEN 1
                        ELSE 0
                    END
                ) AS high_risks
            FROM departments d
            LEFT JOIN risks r
                ON d.department_id = r.department_id
            WHERE d.department_id=%s
            GROUP BY d.department_id
        """, params)

    departments = cursor.fetchall()

    # ==========================================
    # CATEGORY REPORT
    # ==========================================

    if session["role"] == "Admin":

        cursor.execute("""
            SELECT
                c.category_name,
                COUNT(r.Risk_id) AS total_risks
            FROM risk_categories c
            LEFT JOIN risks r
                ON c.category_id = r.category_id
            GROUP BY c.category_id
            ORDER BY total_risks DESC
        """)

    else:

        cursor.execute("""
            SELECT
                c.category_name,
                COUNT(r.Risk_id) AS total_risks
            FROM risk_categories c
            LEFT JOIN risks r
                ON c.category_id = r.category_id
            WHERE r.department_id=%s
            GROUP BY c.category_id
            ORDER BY total_risks DESC
        """, params)

    categories = cursor.fetchall()

    conn.close()

    return render_template(
    "reports.html",

    total=total,
    high=high,
    medium=medium,
    low=low,

    open_risks=status_counts["open_risks"],
    assigned=status_counts["assigned"],
    under_review=status_counts["under_review"],
    monitoring=status_counts["monitoring"],
    closed=status_counts["closed"],

    departments=departments,
    categories=categories,

    all_departments=all_departments,
    all_categories=all_categories,
    all_statuses=all_statuses,

    selected_department=selected_department,
    selected_category=selected_category,
    selected_status=selected_status
)