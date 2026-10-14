import os
import time
import threading
from flask import Flask, request, redirect
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from config import Config
from models import db, User
from utils.backup import backup_database

csrf = CSRFProtect()


def _start_backup_scheduler(app):
    def loop():
        interval_seconds = max(app.config["BACKUP_INTERVAL_HOURS"], 0.1) * 3600
        while True:
            try:
                backup_database(
                    app.config["BACKUP_SOURCE_PATH"],
                    app.config["BACKUP_DIR"],
                    app.config["BACKUP_RETENTION_COUNT"],
                )
                app.logger.info("Scheduled database backup completed.")
            except Exception as exc:
                app.logger.error(f"Scheduled database backup failed: {exc}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:///"):
        os.makedirs(os.path.dirname(app.config["BACKUP_SOURCE_PATH"]), exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)

    if app.config.get("FORCE_HTTPS"):
        @app.before_request
        def enforce_https():
            if request.headers.get("X-Forwarded-Proto", "http") != "https" and not request.is_secure:
                return redirect(request.url.replace("http://", "https://", 1), code=301)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access your business account."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.inventory import inventory_bp
    from routes.sales import sales_bp
    from routes.expenses import expenses_bp
    from routes.customers import customers_bp
    from routes.reports import reports_bp
    from routes.employees import employees_bp
    from routes.suppliers import suppliers_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(settings_bp)

    with app.app_context():
        db.create_all()

    if app.config.get("BACKUP_ENABLED") and (not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true"):
        _start_backup_scheduler(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)