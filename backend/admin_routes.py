from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from auth import role_required
from cache import clear_cache, get_cache, set_cache
from extensions import db
from models import Application, Company, Drive, Student, User


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def company_json(company):
    return {"id": company.id, "user_id": company.user_id, "name": company.name, "industry": company.industry, "location": company.location, "status": company.approval_status, "active": company.user.is_active}


def student_json(student):
    return {"id": student.id, "user_id": student.user_id, "name": student.full_name, "student_code": student.student_code, "contact": student.contact, "branch": student.branch, "cgpa": student.cgpa, "active": student.user.is_active}


def drive_json(drive):
    return {"id": drive.id, "company": drive.company.name, "title": drive.title, "deadline": drive.application_deadline.isoformat(), "status": drive.status}


@admin_bp.get("/dashboard")
@role_required("Admin")
def dashboard(user):
    cached = get_cache("admin:dashboard")
    if cached:
        return jsonify(cached)
    data = dict(
        students=Student.query.count(), companies=Company.query.count(),
        drives=Drive.query.count(), applications=Application.query.count(),
        shortlisted=Application.query.filter_by(status="Shortlisted").count(),
        selected_placed=Application.query.filter(Application.status.in_(["Selected", "Placed"])).count(),
    )
    set_cache("admin:dashboard", data)
    return jsonify(data)


@admin_bp.get("/companies")
@role_required("Admin")
def companies(user):
    search = request.args.get("q", "").strip()
    key = f"admin:companies:{search.lower()}"
    cached = get_cache(key)
    if cached:
        return jsonify(companies=cached)
    query = Company.query
    if search:
        query = query.filter(or_(Company.name.ilike(f"%{search}%"), Company.industry.ilike(f"%{search}%")))
    rows = [company_json(item) for item in query.order_by(Company.name).all()]
    set_cache(key, rows)
    return jsonify(companies=rows)


@admin_bp.patch("/companies/<int:company_id>/status")
@role_required("Admin")
def company_status(user, company_id):
    company = db.get_or_404(Company, company_id)
    status = (request.get_json() or {}).get("status")
    if status not in ["Pending", "Approved", "Rejected"]:
        return jsonify(message="Invalid company status"), 400
    company.approval_status = status
    db.session.commit()
    clear_cache("admin:", "student:drives", "company:")
    return jsonify(message=f"Company marked {status}")


@admin_bp.get("/students")
@role_required("Admin")
def students(user):
    search = request.args.get("q", "").strip()
    key = f"admin:students:{search.lower()}"
    cached = get_cache(key)
    if cached:
        return jsonify(students=cached)
    query = Student.query
    if search:
        query = query.filter(or_(Student.full_name.ilike(f"%{search}%"), Student.student_code.ilike(f"%{search}%"), Student.contact.ilike(f"%{search}%")))
    rows = [student_json(item) for item in query.order_by(Student.full_name).all()]
    set_cache(key, rows)
    return jsonify(students=rows)


@admin_bp.patch("/users/<int:user_id>/active")
@role_required("Admin")
def user_active(user, user_id):
    target = db.get_or_404(User, user_id)
    if target.role == "Admin":
        return jsonify(message="Admin cannot be deactivated"), 400
    target.is_active = bool((request.get_json() or {}).get("active"))
    db.session.commit()
    clear_cache("admin:")
    return jsonify(message="Account status updated")


@admin_bp.get("/drives")
@role_required("Admin")
def drives(user):
    search = request.args.get("q", "").strip()
    query = Drive.query.join(Company)
    if search:
        query = query.filter(or_(Drive.title.ilike(f"%{search}%"), Company.name.ilike(f"%{search}%")))
    return jsonify(drives=[drive_json(item) for item in query.order_by(Drive.created_at.desc()).all()])


@admin_bp.patch("/drives/<int:drive_id>/status")
@role_required("Admin")
def drive_status(user, drive_id):
    drive = db.get_or_404(Drive, drive_id)
    status = (request.get_json() or {}).get("status")
    if status not in ["Pending", "Approved", "Rejected", "Active", "Closed"]:
        return jsonify(message="Invalid drive status"), 400
    drive.status = status
    db.session.commit()
    clear_cache("admin:", "student:drives", "company:")
    return jsonify(message=f"Drive marked {status}")


@admin_bp.get("/applications")
@role_required("Admin")
def applications(user):
    rows = [{"id": item.id, "student": item.student.full_name, "company": item.drive.company.name, "drive": item.drive.title, "status": item.status} for item in Application.query.order_by(Application.applied_at.desc()).all()]
    return jsonify(applications=rows)
