from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from db import get_db_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if "user_id" in session:
        return redirect("/")

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.*,
                d.department_name
            FROM users u
            LEFT JOIN departments d
                ON u.department_id = d.department_id
            WHERE u.email=%s
        """, (email,))

        user = cursor.fetchone()

        conn.close()

        if user:

            # Prevent inactive users from logging in
            if user["status"] != "Active":
                return "Your account has been deactivated. Please contact the administrator."

            if check_password_hash(user['Password'], password):

                session["user_id"] = user["user_id"]
                session["full_name"] = user["full_name"]
                session["role"] = user["role"]
                session["department_id"] = user["department_id"]
                session["department_name"] = user["department_name"]

                return redirect('/')

        return "Invalid email or password"

    return render_template("login.html")


@auth_bp.route('/logout')
def logout():

    session.clear()

    response = redirect('/login')

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response



from services.email_service import send_email


@auth_bp.route("/test-email")
def test_email():

    send_email(
        recipient="riskmanagementsystem2026@gmail.com",
        subject="Risk Management System",
        body="""
Congratulations!

Your Risk Management System can now send emails successfully.

This is your first test email.
"""
    )

    return "Email Sent Successfully!"
