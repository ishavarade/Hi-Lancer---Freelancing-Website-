import os
from flask import Flask, g
from backend.database.db import init_db, SessionLocal
from backend.app.routes.auth import auth_bp
from backend.app.routes.freelancer import freelancer_bp
from backend.app.routes.client import client_bp
from backend.app.routes.main import main_bp

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "hilancer_secret_production_key_2026")

    # Initialize Database tables
    try:
        init_db()
    except Exception as e:
        print(f"DB Init note: {e}")

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(freelancer_bp)
    app.register_blueprint(client_bp)

    @app.context_processor
    def inject_user():
        from flask import session
        return {
            "current_user_id": session.get("user_id"),
            "current_role": session.get("role"),
            "current_full_name": session.get("full_name")
        }

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
