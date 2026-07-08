from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash

from db import get_db_connection
from services.auth_service import login_required

users_bp = Blueprint("users", __name__)

@users_bp.route("/users")
@login_required
def users():

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            u.user_id,
            u.full_name,
            u.email,
            u.role,
            d.department_name
        FROM users u
        LEFT JOIN departments d
        ON u.department_id = d.department_id
    """)

    users = cursor.fetchall()

    conn.close()

    return render_template("users.html", users=users)

@users_bp.route("/add-user", methods=["GET", "POST"])
@login_required
def add_user():

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        department_id = request.form["department_id"]

        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users
            (full_name, email, Password, role, department_id)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            full_name,
            email,
            hashed_password,
            role,
            department_id
        ))

        conn.commit()
        conn.close()

        return redirect("/users")

    conn.close()

    return render_template(
        "add_user.html",
        departments=departments
    )














































