from datetime import datetime
from pathlib import Path

from flask import Blueprint, Response, current_app, jsonify, request, send_from_directory
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from auth import role_required
from extensions import db
from models import Application, Company, Drive, ExportJob


student_bp = Blueprint("student", __name__, url_prefix="/api/student")


def eligibility(student, drive):
    branches = [item.strip().lower() for item in drive.eligible_branch.split(",")]
    problems = []
    if "all" not in branches and student.branch.lower() not in branches:
        problems.append("Branch is not eligible")
    if student.cgpa < drive.minimum_cgpa:
        problems.append("CGPA is below the minimum")
    if student.graduation_year != drive.graduation_year:
        problems.append("Graduation year is not eligible")
    return problems


def drive_json(drive, student=None):
    data = {"id": drive.id, "company": drive.company.name, "title": drive.title, "description": drive.description, "required_skills": drive.required_skills, "experience": drive.experience, "salary": drive.salary, "benefits": drive.benefits, "eligible_branch": drive.eligible_branch, "minimum_cgpa": drive.minimum_cgpa, "graduation_year": drive.graduation_year, "deadline": drive.application_deadline.isoformat(), "status": drive.status}
    if student:
        problems = eligibility(student, drive)
        data.update(eligible=not problems, eligibility_message=", ".join(problems) or "Eligible")
    return data


def application_json(item):
    return {"id": item.id, "company": item.drive.company.name, "drive": item.drive.title, "status": item.status, "feedback": item.feedback, "applied_at": item.applied_at.isoformat(), "interview": {"scheduled_at": item.interview.scheduled_at.isoformat(), "mode": item.interview.mode, "meeting_details": item.interview.meeting_details, "notes": item.interview.notes} if item.interview else None}


@student_bp.route("/profile", methods=["GET", "PATCH"])
@role_required("Student")
def profile(user):
    student = user.student
    if request.method == "PATCH":
        data = request.get_json() or {}
        for field in ["full_name", "student_code", "contact", "branch", "education", "skills", "experience"]:
            if field in data:
                setattr(student, field, str(data[field]).strip())
        try:
            if "cgpa" in data: student.cgpa = float(data["cgpa"])
            if "graduation_year" in data: student.graduation_year = int(data["graduation_year"])
            if not 0 <= student.cgpa <= 10: raise ValueError
        except (ValueError, TypeError):
            return jsonify(message="CGPA or graduation year is invalid"), 400
        db.session.commit()
    return jsonify(student={"full_name": student.full_name, "student_code": student.student_code, "contact": student.contact, "branch": student.branch, "cgpa": student.cgpa, "graduation_year": student.graduation_year, "education": student.education, "skills": student.skills, "experience": student.experience, "resume_path": student.resume_path})


@student_bp.post("/profile/resume")
@role_required("Student")
def upload_resume(user):
    file = request.files.get("resume")
    if not file or not file.filename.lower().endswith(".pdf"):
        return jsonify(message="Please upload a PDF resume"), 400
    folder = Path(current_app.root_path) / "uploads"
    folder.mkdir(exist_ok=True)
    filename = f"student_{user.student.id}_{secure_filename(file.filename)}"
    file.save(folder / filename)
    user.student.resume_path = filename
    db.session.commit()
    return jsonify(message="Resume uploaded", resume_path=filename)


@student_bp.get("/drives")
@role_required("Student")
def drives(user):
    search = request.args.get("q", "").strip()
    query = Drive.query.join(Company).filter(Drive.status.in_(["Approved", "Active"]), Drive.application_deadline >= datetime.now())
    if search:
        query = query.filter(or_(Company.name.ilike(f"%{search}%"), Drive.title.ilike(f"%{search}%"), Drive.required_skills.ilike(f"%{search}%")))
    return jsonify(drives=[drive_json(item, user.student) for item in query.order_by(Drive.application_deadline).all()])


@student_bp.post("/drives/<int:drive_id>/apply")
@role_required("Student")
def apply(user, drive_id):
    drive = db.get_or_404(Drive, drive_id)
    if drive.status not in ["Approved", "Active"] or drive.application_deadline < datetime.now():
        return jsonify(message="Drive is not approved and open"), 400
    problems = eligibility(user.student, drive)
    if problems:
        return jsonify(message=", ".join(problems)), 400
    if Application.query.filter_by(student_id=user.student.id, drive_id=drive.id).first():
        return jsonify(message="You have already applied to this drive"), 409
    application = Application(student_id=user.student.id, drive_id=drive.id)
    try:
        db.session.add(application); db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(message="You have already applied to this drive"), 409
    return jsonify(message="Application submitted", application=application_json(application)), 201


@student_bp.get("/applications")
@role_required("Student")
def applications(user):
    rows = Application.query.filter_by(student_id=user.student.id).order_by(Application.applied_at.desc()).all()
    return jsonify(applications=[application_json(item) for item in rows])


@student_bp.get("/placements")
@role_required("Student")
def placements(user):
    rows = [{"id": item.id, "company": item.company.name, "position": item.position, "salary": item.salary, "joining_date": item.joining_date.isoformat() if item.joining_date else None, "status": item.application.status} for item in user.student.placements]
    return jsonify(placements=rows)


@student_bp.get("/placements/<int:placement_id>/confirmation")
@role_required("Student")
def placement_confirmation(user, placement_id):
    placement = next((item for item in user.student.placements if item.id == placement_id), None)
    if not placement:
        return jsonify(message="Placement record not found"), 404
    text = f"PLACEMENT CONFIRMATION\n\nStudent: {user.student.full_name}\nStudent ID: {user.student.student_code}\nCompany: {placement.company.name}\nPosition: {placement.position}\nSalary: {placement.salary}\nStatus: {placement.application.status}\n"
    return Response(text, mimetype="text/plain", headers={"Content-Disposition": f"attachment; filename=placement_{placement.id}.txt"})


@student_bp.post("/exports")
@role_required("Student")
def start_export(user):
    job = ExportJob(student_id=user.student.id)
    db.session.add(job); db.session.commit()
    if current_app.config.get("TESTING"):
        from tasks import create_export
        create_export(user.student.id, job.id)
    else:
        from tasks import export_student_history
        export_student_history.delay(user.student.id, job.id)
    return jsonify(message="CSV export started", job_id=job.id), 202


@student_bp.get("/exports/<int:job_id>")
@role_required("Student")
def export_status(user, job_id):
    job = db.get_or_404(ExportJob, job_id)
    if job.student_id != user.student.id:
        return jsonify(message="Export not found"), 404
    return jsonify(id=job.id, status=job.status, filename=job.filename)


@student_bp.get("/exports/<int:job_id>/download")
@role_required("Student")
def download_export(user, job_id):
    job = db.get_or_404(ExportJob, job_id)
    if job.student_id != user.student.id or job.status != "Completed":
        return jsonify(message="Export is not ready"), 404
    return send_from_directory(Path(current_app.root_path) / "exports", job.filename, as_attachment=True)
