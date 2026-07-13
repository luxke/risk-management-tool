from flask import Flask

app = Flask(__name__)
app.secret_key = "RiskManagementSecretKey2026"

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.risks import risks_bp
from routes.users import users_bp
from routes.departments import departments_bp
from routes.categories import categories_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(risks_bp)
app.register_blueprint(users_bp)
app.register_blueprint(departments_bp)
app.register_blueprint(categories_bp)

if __name__ == "__main__":
    app.run(debug=True)














