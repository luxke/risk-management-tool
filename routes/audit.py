from flask import Blueprint, render_template, session
from db import get_db_connection
from services.auth_service import login_required

audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/risk-history/<int:risk_id>")
@login_required
def risk_history(risk_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            ra.audit_id,
            ra.action_taken,
            ra.change_date,
            u.full_name
        FROM risk_audit ra
        LEFT JOIN users u
            ON ra.changed_by = u.user_id
        WHERE ra.risk_id = %s
        ORDER BY ra.change_date DESC
    """, (risk_id,))

    history = cursor.fetchall()

    conn.close()

    return render_template(
        "risk_history.html",
        history=history,
        risk_id=risk_id
    )