import csv
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from pathlib import Path

from celery import Celery, Task
from celery.schedules import crontab
from flask import render_template_string

from app import create_app
from extensions import db
from models import Application, Drive, ExportJob, Interview, Placement, Student, User


flask_app = create_app()


class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)


celery = Celery("placement_tasks", task_cls=FlaskTask)
celery.conf.update(
    broker_url=flask_app.config["CELERY_BROKER_URL"],
    result_backend=flask_app.config["CELERY_RESULT_BACKEND"],
    timezone="Asia/Kolkata",
    beat_schedule={
        "daily-student-reminders": {"task": "tasks.daily_reminders", "schedule": crontab(hour=9, minute=0)},
        "monthly-admin-report": {"task": "tasks.monthly_report", "schedule": crontab(day_of_month=1, hour=8, minute=0)},
    },
)


def output_folder(name):
    folder = Path(flask_app.root_path) / name
    folder.mkdir(exist_ok=True)
    return folder


def send_email(recipient, subject, body, html=False):
    """SMTP na ho to local reports folder mein email save hoti hai."""
    if not flask_app.config["MAIL_SERVER"]:
        suffix = "html" if html else "txt"
        filename = f"mail_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.{suffix}"
        (output_folder("reports") / filename).write_text(body, encoding="utf-8")
        return filename
    message = EmailMessage()
    message["From"] = flask_app.config["MAIL_SENDER"]
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body if not html else "Please view this report in HTML format.")
    if html:
        message.add_alternative(body, subtype="html")
    with smtplib.SMTP(flask_app.config["MAIL_SERVER"], flask_app.config["MAIL_PORT"]) as server:
        server.starttls()
        if flask_app.config["MAIL_USERNAME"]:
            server.login(flask_app.config["MAIL_USERNAME"], flask_app.config["MAIL_PASSWORD"])
        server.send_message(message)
    return "sent"


@celery.task(name="tasks.daily_reminders")
def daily_reminders():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    sent = 0
    for student in Student.query.all():
        deadlines = Drive.query.filter(Drive.status.in_(["Approved", "Active"]), Drive.application_deadline.between(now, tomorrow)).all()
        interviews = Interview.query.join(Application).filter(Application.student_id == student.id, Interview.scheduled_at.between(now, tomorrow)).all()
        if deadlines or interviews:
            lines = [f"Hello {student.full_name},", ""]
            lines += [f"Deadline: {drive.company.name} - {drive.title} at {drive.application_deadline}" for drive in deadlines]
            lines += [f"Interview: {item.application.drive.title} at {item.scheduled_at} ({item.mode})" for item in interviews]
            send_email(student.user.email, "Placement Portal Daily Reminder", "\n".join(lines))
            sent += 1
    return {"students_notified": sent}


@celery.task(name="tasks.monthly_report")
def monthly_report():
    admin = User.query.filter_by(role="Admin").first()
    data = {"drives": Drive.query.count(), "applications": Application.query.count(), "shortlisted": Application.query.filter_by(status="Shortlisted").count(), "selected": Application.query.filter(Application.status.in_(["Selected", "Placed"])).count()}
    html = render_template_string("""<h1>Monthly Placement Activity Report</h1><p>Generated: {{ date }}</p><table border=\"1\" cellpadding=\"8\"><tr><th>Drives</th><th>Applications</th><th>Shortlisted</th><th>Selected/Placed</th></tr><tr><td>{{ d.drives }}</td><td>{{ d.applications }}</td><td>{{ d.shortlisted }}</td><td>{{ d.selected }}</td></tr></table>""", date=datetime.now().date(), d=data)
    filename = f"monthly_report_{datetime.now().strftime('%Y_%m')}.html"
    (output_folder("reports") / filename).write_text(html, encoding="utf-8")
    if admin:
        send_email(admin.email, "Monthly Placement Activity Report", html, html=True)
    return {"filename": filename, **data}


def create_export(student_id, job_id):
    student = db.session.get(Student, student_id)
    job = db.session.get(ExportJob, job_id)
    filename = f"applications_student_{student.id}_job_{job.id}.csv"
    path = output_folder("exports") / filename
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Student ID", "Company", "Drive", "Status", "Applied Date"])
        for item in student.applications:
            writer.writerow([student.student_code, item.drive.company.name, item.drive.title, item.status, item.applied_at.isoformat()])
    job.status = "Completed"; job.filename = filename; db.session.commit()
    send_email(student.user.email, "CSV Export Completed", f"Your application history export is ready: {filename}")
    return filename


@celery.task(name="tasks.export_student_history")
def export_student_history(student_id, job_id):
    return create_export(student_id, job_id)
