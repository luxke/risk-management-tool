from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection
from services.auth_service import login_required

departments_bp = Blueprint("departments", __name__)


# ===============================
# View Departments
# ===============================
@departments_bp.route("/departments")
@login_required
def departments():

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM departments
        ORDER BY department_name
    """)

    departments = cursor.fetchall()

    conn.close()

    return render_template(
        "departments.html",
        departments=departments
    )


# ===============================
# Add Department
# ===============================
@departments_bp.route("/add-department", methods=["GET", "POST"])
@login_required
def add_department():

    if session["role"] != "Admin":
        return "Access Denied", 403

    if request.method == "POST":

        department_name = request.form["department_name"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO departments (department_name)
            VALUES (%s)
        """, (department_name,))

        conn.commit()
        conn.close()

        return redirect("/departments")

    return render_template("add_department.html")


# ===============================
# Edit Department
# ===============================
@departments_bp.route("/edit-department/<int:department_id>", methods=["GET", "POST"])
@login_required
def edit_department(department_id):

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM departments
        WHERE department_id = %s
    """, (department_id,))

    department = cursor.fetchone()

    if request.method == "POST":

        department_name = request.form["department_name"]

        cursor.execute("""
            UPDATE departments
            SET department_name = %s
            WHERE department_id = %s
        """, (department_name, department_id))

        conn.commit()
        conn.close()

        return redirect("/departments")

    conn.close()

    return render_template(
        "edit_department.html",
        department=department
    )


# ===============================
# Delete Department
# ===============================
@departments_bp.route("/delete-department/<int:department_id>")
@login_required
def delete_department(department_id):

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM departments
        WHERE department_id = %s
    """, (department_id,))

    conn.commit()
    conn.close()

    return redirect("/departments")