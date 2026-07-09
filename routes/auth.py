from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from db import get_db_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user['Password'], password):

            session['user_id'] = user['user_id']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session["department_id"] = user["department_id"]
            
            return redirect('/')

        return "Invalid email or password"

    return render_template("login.html")


@auth_bp.route('/logout')
def logout():

    session.clear()

    return redirect('/login')