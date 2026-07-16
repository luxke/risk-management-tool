from flask import session
from db import get_db_connection


def notification_count():

    if "user_id" not in session:
        return dict(unread_notifications=0)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE user_id=%s
        AND is_read=0
    """, (session["user_id"],))

    total = cursor.fetchone()["total"]

    conn.close()

    return dict(unread_notifications=total)