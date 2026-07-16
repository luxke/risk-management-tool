from flask import Blueprint, render_template, session, redirect
from db import get_db_connection
from services.auth_service import login_required

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/notifications")
@login_required
def notifications():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            notification_id,
            message,
            is_read,
            created_at
        FROM notifications
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (session["user_id"],))

    notifications = cursor.fetchall()

    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications
    )

from flask import redirect

@notifications_bp.route("/mark-notification/<int:notification_id>")
@login_required
def mark_notification(notification_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notifications
        SET is_read = 1
        WHERE notification_id = %s
        AND user_id = %s
    """, (notification_id, session["user_id"]))

    conn.commit()
    conn.close()

    return redirect("/notifications")



