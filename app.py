from flask import Flask

app = Flask(__name__)
app.secret_key = "RiskManagementSecretKey2026"

from services.context_processor import notification_count
app.context_processor(notification_count)
    
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.risks import risks_bp
from routes.users import users_bp
from routes.departments import departments_bp
from routes.categories import categories_bp
from routes.audit import audit_bp
from routes.reports import reports_bp
from routes.notifications import notifications_bp   


app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(risks_bp)
app.register_blueprint(users_bp)
app.register_blueprint(departments_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(audit_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(notifications_bp)


if __name__ == "__main__":
    app.run(debug=True)














