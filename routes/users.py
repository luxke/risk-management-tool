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
            u.status,       
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


@users_bp.route("/edit-user/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM users WHERE user_id=%s",
        (user_id,)
    )

    user = cursor.fetchone()

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        role = request.form["role"]
        department_id = request.form["department_id"]

        cursor.execute("""
            UPDATE users
            SET
                full_name=%s,
                email=%s,
                role=%s,
                department_id=%s
            WHERE user_id=%s
        """, (
            full_name,
            email,
            role,
            department_id,
            user_id
        ))

        conn.commit()
        conn.close()

        return redirect("/users")

    conn.close()

    return render_template(
        "edit_user.html",
        user=user,
        departments=departments
    )

@users_bp.route("/deactivate-user/<int:user_id>")
@login_required
def deactivate_user(user_id):

    if session["role"] != "Admin":
        return "Access Denied", 403

    if session["user_id"] == user_id:
        return "You cannot deactivate your own account."

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET status='Inactive'
        WHERE user_id=%s
    """, (user_id,))

    conn.commit()
    conn.close()

    return redirect("/users")


@users_bp.route("/activate-user/<int:user_id>")
@login_required
def activate_user(user_id):

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET status='Active'
        WHERE user_id=%s
    """, (user_id,))

    conn.commit()
    conn.close()

    return redirect("/users")








































