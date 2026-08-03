from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection
from services.auth_service import login_required
from services.email_service import send_email

communications_bp = Blueprint("communications", __name__)


# ======================================
# View Communications
# ======================================
@communications_bp.route("/communications")
@login_required
def communications():

    # Only Risk Managers can manage communications
    if session["role"] != "Risk Manager":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.*,
            d.department_name
        FROM communications c
        LEFT JOIN departments d
            ON c.department_id = d.department_id
        ORDER BY c.created_at DESC
    """)

    communications = cursor.fetchall()

    conn.close()

    return render_template(
        "communications.html",
        communications=communications
    )


# ======================================
# Create Communication
# ======================================
@communications_bp.route("/add-communication", methods=["GET", "POST"])
@login_required
def add_communication():

    if session["role"] != "Risk Manager":
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

    # --------------------------------------
    # Save Communication
    # --------------------------------------
    if request.method == "POST":

        title = request.form["title"]
        message = request.form["message"]
        communication_type = request.form["communication_type"]

        # Empty value means all departments
        department_id = request.form.get("department_id") or None

        send_email_option = request.form.get("send_email")
        send_email_flag = 1 if send_email_option else 0

        # Save communication
        cursor.execute("""
            INSERT INTO communications
            (
                title,
                message,
                communication_type,
                department_id,
                send_email,
                created_by
            )
            VALUES
            (%s,%s,%s,%s,%s,%s)
        """, (
            title,
            message,
            communication_type,
            department_id,
            send_email_flag,
            session["user_id"]
        ))

        communication_id = cursor.lastrowid

        # --------------------------------------
        # Get recipients
        # --------------------------------------
        if department_id:

            cursor.execute("""
                SELECT
                    user_id,
                    full_name,
                    email
                FROM users
                WHERE
                    department_id=%s
                    AND status='Active'
            """, (department_id,))

        else:

            cursor.execute("""
                SELECT
                    user_id,
                    full_name,
                    email
                FROM users
                WHERE status='Active'
            """)

        recipients = cursor.fetchall()

        # --------------------------------------
        # Create notifications and send emails
        # --------------------------------------
        for user in recipients:

            # Dashboard notification
            cursor.execute("""
                INSERT INTO notifications
                (
                    user_id,
                    message
                )
                VALUES
                (%s,%s)
            """, (
                user["user_id"],
                f"New {communication_type}: {title}"
            ))

            # Email notification
            if send_email_flag:

                html = render_template(
                    "emails/communication.html",
                    recipient_name=user["full_name"],
                    title=title,
                    communication_type=communication_type,
                    message=message,
                    url="http://127.0.0.1:5000/communications"
                )

                send_email(
                    recipient=user["email"],
                    subject=title,
                    html=html
                )

        conn.commit()
        conn.close()

        return redirect("/communications")

    conn.close()

    return render_template(
        "add_communication.html",
        departments=departments
    )