from flask import Flask, jsonify

from config import Config
from extensions import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)
    if app.config.get("TESTING") and "CACHE_ENABLED" not in (test_config or {}):
        app.config["CACHE_ENABLED"] = False

    db.init_app(app)

    from auth_routes import auth_bp
    from admin_routes import admin_bp
    from company_routes import company_bp
    from student_routes import student_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    @app.get("/api/health")
    def health():
        return jsonify(message="Placement Portal API is running")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
