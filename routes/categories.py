from flask import Blueprint, render_template, request, redirect, session
from db import get_db_connection
from services.auth_service import login_required

categories_bp = Blueprint("categories", __name__)


# =====================================
# View Categories
# =====================================
@categories_bp.route("/categories")
@login_required
def categories():

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM risk_categories
        ORDER BY category_name
    """)

    categories = cursor.fetchall()

    conn.close()

    return render_template(
        "categories.html",
        categories=categories
    )


# =====================================
# Add Category
# =====================================
@categories_bp.route("/add-category", methods=["GET", "POST"])
@login_required
def add_category():

    if session["role"] != "Admin":
        return "Access Denied", 403

    if request.method == "POST":

        category_name = request.form["category_name"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO risk_categories (category_name)
            VALUES (%s)
        """, (category_name,))

        conn.commit()
        conn.close()

        return redirect("/categories")

    return render_template("add_category.html")


# =====================================
# Edit Category
# =====================================
@categories_bp.route("/edit-category/<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM risk_categories
        WHERE category_id = %s
    """, (category_id,))

    category = cursor.fetchone()

    if request.method == "POST":

        category_name = request.form["category_name"]

        cursor.execute("""
            UPDATE risk_categories
            SET category_name = %s
            WHERE category_id = %s
        """, (
            category_name,
            category_id
        ))

        conn.commit()
        conn.close()

        return redirect("/categories")

    conn.close()

    return render_template(
        "edit_category.html",
        category=category
    )


# =====================================
# Delete Category
# =====================================
@categories_bp.route("/delete-category/<int:category_id>")
@login_required
def delete_category(category_id):

    if session["role"] != "Admin":
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM risk_categories
        WHERE category_id = %s
    """, (category_id,))

    conn.commit()
    conn.close()

    return redirect("/categories")