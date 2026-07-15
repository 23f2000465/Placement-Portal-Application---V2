from flask import Blueprint, jsonify, request, session
from sqlalchemy.exc import IntegrityError

from auth import role_required
from cache import clear_cache
from extensions import db
from models import Company, Student, User


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def required(data, fields):
    return [field for field in fields if data.get(field) in (None, "")]


def user_data(user):
    profile_id = user.company.id if user.company else user.student.id if user.student else None
    return {"id": user.id, "email": user.email, "role": user.role, "profile_id": profile_id}


@auth_bp.post("/register/student")
def register_student():
    data = request.get_json() or {}
    fields = ["email", "password", "full_name", "student_code", "contact", "branch", "cgpa", "graduation_year"]
    missing = required(data, fields)
    if missing:
        return jsonify(message=f"Required: {', '.join(missing)}"), 400
    if len(data["password"]) < 6:
        return jsonify(message="Password must have at least 6 characters"), 400
    try:
        cgpa = float(data["cgpa"])
        year = int(data["graduation_year"])
        if not 0 <= cgpa <= 10:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify(message="CGPA must be 0-10 and graduation year must be valid"), 400

    user = User(email=data["email"].strip().lower(), role="Student")
    user.set_password(data["password"])
    user.student = Student(
        full_name=data["full_name"].strip(), student_code=data["student_code"].strip(),
        contact=data["contact"].strip(), branch=data["branch"].strip(), cgpa=cgpa,
        graduation_year=year,
    )
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(message="Email or student ID already exists"), 409
    clear_cache("admin:")
    return jsonify(message="Student registered successfully"), 201


@auth_bp.post("/register/company")
def register_company():
    data = request.get_json() or {}
    fields = ["email", "password", "name", "industry", "location", "hr_contact"]
    missing = required(data, fields)
    if missing:
        return jsonify(message=f"Required: {', '.join(missing)}"), 400
    if len(data["password"]) < 6:
        return jsonify(message="Password must have at least 6 characters"), 400

    user = User(email=data["email"].strip().lower(), role="Company")
    user.set_password(data["password"])
    user.company = Company(
        name=data["name"].strip(), industry=data["industry"].strip(),
        location=data["location"].strip(), hr_contact=data["hr_contact"].strip(),
        website=data.get("website", "").strip(),
    )
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(message="Email already exists"), 409
    clear_cache("admin:")
    return jsonify(message="Company registered; admin approval is pending"), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email", "").strip().lower()).first()
    if not user or not user.check_password(data.get("password", "")):
        return jsonify(message="Invalid email or password"), 401
    if not user.is_active:
        return jsonify(message="Account is deactivated"), 403
    session.clear()
    session["user_id"] = user.id
    return jsonify(message="Login successful", user=user_data(user))


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify(message="Logged out")


@auth_bp.get("/me")
@role_required("Admin", "Company", "Student")
def me(user):
    return jsonify(user=user_data(user))
