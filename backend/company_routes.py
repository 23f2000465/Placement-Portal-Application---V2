from datetime import date, datetime

from flask import Blueprint, jsonify, request

from auth import role_required
from cache import clear_cache, get_cache, set_cache
from extensions import db
from models import Application, Drive, Interview, Placement


company_bp = Blueprint("company", __name__, url_prefix="/api/company")


def own_drive(user, drive_id):
    drive = db.get_or_404(Drive, drive_id)
    return drive if drive.company_id == user.company.id else None


def drive_json(drive):
    return {
        "id": drive.id, "title": drive.title, "description": drive.description,
        "required_skills": drive.required_skills, "experience": drive.experience,
        "salary": drive.salary, "benefits": drive.benefits, "eligible_branch": drive.eligible_branch,
        "minimum_cgpa": drive.minimum_cgpa, "graduation_year": drive.graduation_year,
        "application_deadline": drive.application_deadline.isoformat(), "status": drive.status,
        "applicants": len(drive.applications),
    }


@company_bp.get("/dashboard")
@role_required("Company")
def dashboard(user):
    key = f"company:dashboard:{user.company.id}"
    cached = get_cache(key)
    if cached:
        return jsonify(cached)
    applications = Application.query.join(Drive).filter(Drive.company_id == user.company.id)
    data = dict(
        approval_status=user.company.approval_status, drives=len(user.company.drives),
        applicants=applications.count(), selected=applications.filter(Application.status.in_(["Shortlisted", "Selected", "Placed"])).count(),
    )
    set_cache(key, data)
    return jsonify(data)


@company_bp.route("/profile", methods=["GET", "PATCH"])
@role_required("Company")
def profile(user):
    company = user.company
    if request.method == "PATCH":
        data = request.get_json() or {}
        for field in ["name", "industry", "location", "hr_contact", "website"]:
            if field in data:
                setattr(company, field, str(data[field]).strip())
        if not all([company.name, company.industry, company.location, company.hr_contact]):
            return jsonify(message="Name, industry, location and HR contact are required"), 400
        db.session.commit()
    return jsonify(company={"name": company.name, "industry": company.industry, "location": company.location, "hr_contact": company.hr_contact, "website": company.website, "approval_status": company.approval_status})


@company_bp.route("/drives", methods=["GET", "POST"])
@role_required("Company")
def drives(user):
    if request.method == "GET":
        return jsonify(drives=[drive_json(item) for item in Drive.query.filter_by(company_id=user.company.id).order_by(Drive.created_at.desc()).all()])
    if user.company.approval_status != "Approved":
        return jsonify(message="Admin approval is required before creating a drive"), 403
    data = request.get_json() or {}
    required = ["title", "description", "required_skills", "salary", "eligible_branch", "minimum_cgpa", "graduation_year", "application_deadline"]
    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        return jsonify(message=f"Required: {', '.join(missing)}"), 400
    try:
        drive = Drive(
            company_id=user.company.id, title=data["title"].strip(), description=data["description"].strip(),
            required_skills=data["required_skills"].strip(), experience=data.get("experience", "Fresher").strip(),
            salary=float(data["salary"]), benefits=data.get("benefits", "").strip(),
            eligible_branch=data["eligible_branch"].strip(), minimum_cgpa=float(data["minimum_cgpa"]),
            graduation_year=int(data["graduation_year"]), application_deadline=datetime.fromisoformat(data["application_deadline"]),
        )
    except (ValueError, TypeError):
        return jsonify(message="Salary, CGPA, year or deadline is invalid"), 400
    db.session.add(drive); db.session.commit()
    clear_cache("admin:", "student:drives", "company:")
    return jsonify(message="Drive created and sent for admin approval", drive=drive_json(drive)), 201


@company_bp.route("/drives/<int:drive_id>", methods=["PATCH", "DELETE"])
@role_required("Company")
def update_drive(user, drive_id):
    drive = own_drive(user, drive_id)
    if not drive:
        return jsonify(message="This drive does not belong to your company"), 403
    if request.method == "DELETE":
        if drive.applications:
            return jsonify(message="Drive with applications cannot be deleted; close it instead"), 409
        db.session.delete(drive); db.session.commit(); clear_cache("admin:", "student:drives", "company:")
        return jsonify(message="Drive deleted")
    data = request.get_json() or {}
    if data.get("status") in ["Active", "Closed"]:
        if drive.status not in ["Approved", "Active", "Closed"]:
            return jsonify(message="Only an approved drive can be activated or closed"), 400
        drive.status = data["status"]
    for field in ["title", "description", "required_skills", "experience", "benefits"]:
        if field in data:
            setattr(drive, field, str(data[field]).strip())
    db.session.commit()
    clear_cache("admin:", "student:drives", "company:")
    return jsonify(message="Drive updated", drive=drive_json(drive))


@company_bp.get("/drives/<int:drive_id>/applicants")
@role_required("Company")
def applicants(user, drive_id):
    drive = own_drive(user, drive_id)
    if not drive:
        return jsonify(message="This drive does not belong to your company"), 403
    rows = []
    for item in drive.applications:
        student = item.student
        rows.append({"application_id": item.id, "status": item.status, "feedback": item.feedback, "student": {"name": student.full_name, "student_code": student.student_code, "contact": student.contact, "branch": student.branch, "cgpa": student.cgpa, "skills": student.skills, "education": student.education, "experience": student.experience}, "interview": {"scheduled_at": item.interview.scheduled_at.isoformat(), "mode": item.interview.mode, "meeting_details": item.interview.meeting_details, "notes": item.interview.notes} if item.interview else None})
    return jsonify(applicants=rows)


@company_bp.patch("/applications/<int:application_id>")
@role_required("Company")
def application_status(user, application_id):
    application = db.get_or_404(Application, application_id)
    if application.drive.company_id != user.company.id:
        return jsonify(message="This application does not belong to your drive"), 403
    data = request.get_json() or {}
    status = data.get("status")
    if status not in ["Applied", "Shortlisted", "Interview", "Selected", "Rejected", "Placed"]:
        return jsonify(message="Invalid application status"), 400
    application.status = status
    application.feedback = data.get("feedback", application.feedback).strip()
    if status in ["Selected", "Placed"] and not application.placement:
        joining_date = None
        if data.get("joining_date"):
            try:
                joining_date = date.fromisoformat(data["joining_date"])
            except ValueError:
                return jsonify(message="Joining date is invalid"), 400
        placement = Placement(
            application_id=application.id, student_id=application.student_id,
            company_id=application.drive.company_id, position=application.drive.title,
            salary=application.drive.salary, joining_date=joining_date,
        )
        db.session.add(placement)
    db.session.commit()
    clear_cache("admin:", "company:")
    return jsonify(message="Application updated")


@company_bp.post("/applications/<int:application_id>/interview")
@role_required("Company")
def schedule_interview(user, application_id):
    application = db.get_or_404(Application, application_id)
    if application.drive.company_id != user.company.id:
        return jsonify(message="This application does not belong to your drive"), 403
    data = request.get_json() or {}
    try:
        scheduled_at = datetime.fromisoformat(data["scheduled_at"])
    except (KeyError, TypeError, ValueError):
        return jsonify(message="Valid interview date and time is required"), 400
    if not data.get("mode") or not data.get("meeting_details"):
        return jsonify(message="Mode and meeting link/venue are required"), 400
    interview = application.interview or Interview(application_id=application.id)
    interview.scheduled_at = scheduled_at
    interview.mode = data["mode"].strip()
    interview.meeting_details = data["meeting_details"].strip()
    interview.notes = data.get("notes", "").strip()
    application.status = "Interview"
    db.session.add(interview); db.session.commit()
    clear_cache("admin:", "company:")
    return jsonify(message="Interview scheduled")
