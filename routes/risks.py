from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection
from services.auth_service import login_required

risks_bp = Blueprint("risks", __name__)


@risks_bp.route("/add-risk", methods=["GET", "POST"])
@login_required
def add_risk():

    # Only Admin and Risk Manager can create risks
    if session["role"] not in ["Admin","Risk Manager"]:
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ==========================
    # Load Departments
    # ==========================
    if session["role"] == "Admin":

        cursor.execute("""
            SELECT *
            FROM departments
            ORDER BY department_name
        """)

    else:

        cursor.execute("""
            SELECT *
            FROM departments
            WHERE department_id = %s
        """, (session["department_id"],))

    departments = cursor.fetchall()

    # ==========================
    # Load Categories
    # ==========================
    cursor.execute("""
        SELECT *
        FROM risk_categories
        ORDER BY category_name
    """)

    categories = cursor.fetchall()

    # ==========================
    # Save Risk
    # ==========================
    if request.method == "POST":

        title = request.form["Tittle"]
        description = request.form["description"]
        probability = int(request.form["probability"])
        impact = int(request.form["impact"])
        risk_reference = request.form["risk_reference"]
        strategic_objective = request.form["strategic_objective"]
        cause_of_risk = request.form["cause_of_risk"]
        key_risk_indicator = request.form["key_risk_indicator"]
        existing_controls = request.form["existing_controls"]
        risk_appetite = request.form["risk_appetite"]
        control_effectiveness = request.form["control_effectiveness"]
        control_owner = request.form["control_owner"]
        treatment_strategy = request.form["treatment_strategy"]
        action_plan = request.form["action_plan"]
        review_date = request.form["review_date"]
        target_closure_date = request.form["target_closure_date"]
        residual_probability = request.form["residual_probability"] or None
        residual_impact = request.form["residual_impact"] or None
        residual_score = request.form["residual_score"] or None

        # Department
        if session["role"] == "Admin":
            department_id = request.form["department_id"]
        else:
            department_id = session["department_id"]

        # Category
        category_id = request.form["category_id"]

        score = probability * impact

        created_by = session["user_id"]

        cursor.execute("""
            INSERT INTO risks
            (
                risk_reference,
                strategic_objective,
                Tittle,
                Description,
                cause_of_risk,
                Probability,
                Impact,
                Score,
                key_risk_indicator,
                existing_controls,
                risk_appetite,
                control_effectiveness
                control_owner
                treatment_strategy
                action_plan
                review_date
                target_closure_date            
                residual_probability
                residual_impact
                residual_score                     
                status_id,
                Owner_id,
                department_id,
                category_id,
                created_by
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            risk_reference,
            strategic_objective,
            title,
            description,
            cause_of_risk,
            probability,
            impact,
            score,
            key_risk_indicator,
            existing_controls,
            risk_appetite,
            control_effectiveness,
            control_owner,
            treatment_strategy,
            action_plan,
            review_date,
            target_closure_date,
            residual_probability,
            residual_impact,
            residual_score,
            1,          # Open
            None,       # No owner yet
            department_id,
            category_id,
            created_by
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

        # Assign employee and change status to Assigned
        cursor.execute("""
            UPDATE risks
            SET
                Owner_id=%s,
                status_id=2
            WHERE Risk_id=%s
        """, (
            owner_id,
            risk_id
        ))

        # Create notification
        cursor.execute("""
            INSERT INTO notifications
            (
                user_id,
                risk_id,
                message
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
        """, (
            owner_id,
            risk_id,
            f"You have been assigned Risk #{risk_id}. Please review and begin mitigation."
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

@risks_bp.route("/update-risk/<int:risk_id>", methods=["GET", "POST"])
@login_required
def update_risk(risk_id):

    # Only employees can update risks
    if session["role"] != "Employee":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Load the employee's assigned risk
    cursor.execute("""
        SELECT
            r.*,
            d.department_name,
            c.category_name,
            s.status_name
        FROM risks r
        LEFT JOIN departments d
            ON r.department_id = d.department_id
        LEFT JOIN risk_categories c
            ON r.category_id = c.category_id
        LEFT JOIN risk_status s
            ON r.status_id = s.status_id
        WHERE
            r.Risk_id=%s
            AND r.Owner_id=%s
    """, (
        risk_id,
        session["user_id"]
    ))

    risk = cursor.fetchone()

    if not risk:
        conn.close()
        return "Risk not found.", 404

    # Load all statuses
    cursor.execute("""
        SELECT *
        FROM risk_status
        ORDER BY status_id
    """)
    statuses = cursor.fetchall()

    if request.method == "POST":

        status_id = int(request.form["status_id"])
        progress_notes = request.form["progress_notes"]

        # ---------------------------------
        # Get old status name
        # ---------------------------------
        cursor.execute("""
            SELECT status_name
            FROM risk_status
            WHERE status_id=%s
        """, (risk["status_id"],))

        old_status = cursor.fetchone()["status_name"]

        # ---------------------------------
        # Get new status name
        # ---------------------------------
        cursor.execute("""
            SELECT status_name
            FROM risk_status
            WHERE status_id=%s
        """, (status_id,))

        new_status = cursor.fetchone()["status_name"]

        # ---------------------------------
        # Update Risk
        # ---------------------------------
        cursor.execute("""
            UPDATE risks
            SET
                status_id=%s,
                progress_notes=%s
            WHERE Risk_id=%s
        """, (
            status_id,
            progress_notes,
            risk_id
        ))

        # ---------------------------------
        # Build audit message
        # ---------------------------------
        actions = []

        if old_status != new_status:
            actions.append(
                f"Changed status from '{old_status}' to '{new_status}'."
            )

        if progress_notes.strip():
            actions.append("Updated progress notes.")

        # Save audit only if something changed
        if actions:

            cursor.execute("""
                INSERT INTO risk_audit
                (
                    risk_id,
                    action_taken,
                    changed_by
                )
                VALUES (%s,%s,%s)
            """, (
                risk_id,
                " ".join(actions),
                session["user_id"]
            ))

        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()

    return render_template(
        "update_risk.html",
        risk=risk,
        statuses=statuses
    )

@risks_bp.route("/risk-details/<int:risk_id>")
@login_required
def risk_details(risk_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            r.*,

            d.department_name,

            c.category_name,

            rs.status_name,

            u.full_name

        FROM risks r

        LEFT JOIN departments d
            ON r.department_id = d.department_id

        LEFT JOIN risk_categories c
            ON r.category_id = c.category_id

        LEFT JOIN risk_status rs
            ON r.status_id = rs.status_id

        LEFT JOIN users u
            ON r.Owner_id = u.user_id

        WHERE r.Risk_id = %s
    """, (risk_id,))

    risk = cursor.fetchone()

    conn.close()

    if not risk:
        return "Risk not found", 404

    return render_template(
        "risk_details.html",
        risk=risk
    )
