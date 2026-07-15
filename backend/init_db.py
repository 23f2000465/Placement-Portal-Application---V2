import getpass
import os

from app import create_app
from extensions import db
from models import User


def seed_admin(email, password):
    admin = User.query.filter_by(role="Admin").first()
    if admin:
        return admin

    admin = User(email=email.lower(), role="Admin")
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    return admin


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()  # Tables manually nahi, code se create hote hain.
        email = os.getenv("ADMIN_EMAIL") or input("Admin email: ").strip()
        password = os.getenv("ADMIN_PASSWORD") or getpass.getpass("Admin password: ")
        if not email or not password:
            raise ValueError("Admin email and password are required")
        seed_admin(email, password)
        print("Database and admin are ready.")
