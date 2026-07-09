from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection
from services.auth_service import login_required

risks_bp = Blueprint("risks", __name__)


@risks_bp.route("/add-risk", methods=["GET", "POST"])
@login_required
def add_risk():

    # Only Admin can create risks
    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Load departments
    cursor.execute("""
        SELECT *
        FROM departments
        ORDER BY department_name
    """)
    departments = cursor.fetchall()

    # Load categories
    cursor.execute("""
        SELECT *
        FROM risk_categories
        ORDER BY category_name
    """)
    categories = cursor.fetchall()

    if request.method == "POST":

        title = request.form["Tittle"]
        description = request.form["description"]
        probability = int(request.form["probability"])
        impact = int(request.form["impact"])

        department_id = request.form["department_id"]
        category_id = request.form["category_id"]

        score = probability * impact

        cursor.execute("""
            INSERT INTO risks
            (
                Tittle,
                Description,
                Probability,
                Impact,
                Score,
                status,
                Owner_id,
                department_id,
                category_id
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            title,
            description,
            probability,
            impact,
            score,
            "Open",
            None,
            department_id,
            category_id
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()

    return render_template(
        "add_risk.html",
        departments=departments,
        categories=categories
    )

@risks_bp.route("/assign-risk/<int:risk_id>", methods=["GET", "POST"])
@login_required
def assign_risk(risk_id):

     if session["role"] != "Risk Manager":
        return "Access Denied", 403

     conn = get_db_connection()
     cursor = conn.cursor(dictionary=True)

     # Get the selected risk
     cursor.execute("""
        SELECT *
        FROM risks
        WHERE Risk_id=%s
     """, (risk_id,))

     risk = cursor.fetchone()

     # Security check
     if risk["department_id"] != session["department_id"]:
        conn.close()
        return "Access Denied", 403

     # Get employees in this department
     cursor.execute("""
        SELECT
            user_id,
            full_name
        FROM users
        WHERE
            department_id=%s
            AND role='Employee'
            AND status='Active'
        ORDER BY full_name
     """, (session["department_id"],))

     employees = cursor.fetchall()

     if request.method == "POST":

        owner_id = request.form["owner_id"]

        cursor.execute("""
            UPDATE risks
            SET
                Owner_id=%s,
                status='Assigned'
            WHERE Risk_id=%s
        """, (
            owner_id,
            risk_id
        ))

        conn.commit()
        conn.close()

        return redirect("/")

     conn.close()

     return render_template(
        "assign_risk.html",
        risk=risk,
        employees=employees
     )

@risks_bp.route("/edit-risk/<int:risk_id>", methods=["GET", "POST"])
@login_required
def edit_risk(risk_id):

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Load departments
    cursor.execute("""
        SELECT *
        FROM departments
        ORDER BY department_name
    """)
    departments = cursor.fetchall()

    # Load categories
    cursor.execute("""
        SELECT *
        FROM risk_categories
        ORDER BY category_name
    """)
    categories = cursor.fetchall()

    # Load selected risk
    cursor.execute("""
        SELECT *
        FROM risks
        WHERE Risk_id=%s
    """, (risk_id,))

    risk = cursor.fetchone()

    if request.method == "POST":

        title = request.form["Tittle"]
        description = request.form["description"]
        probability = int(request.form["probability"])
        impact = int(request.form["impact"])
        department_id = request.form["department_id"]
        category_id = request.form["category_id"]

        score = probability * impact

        cursor.execute("""
            UPDATE risks
            SET
                Tittle=%s,
                Description=%s,
                Probability=%s,
                Impact=%s,
                Score=%s,
                department_id=%s,
                category_id=%s
            WHERE Risk_id=%s
        """, (
            title,
            description,
            probability,
            impact,
            score,
            department_id,
            category_id,
            risk_id
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()

    return render_template(
        "edit_risk.html",
        risk=risk,
        departments=departments,
        categories=categories
    )

@risks_bp.route("/delete-risk/<int:risk_id>")
@login_required
def delete_risk(risk_id):

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM risks WHERE Risk_id=%s",
        (risk_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")
