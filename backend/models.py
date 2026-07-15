from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


def current_time():
    return datetime.now(timezone.utc)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=current_time)

    company = db.relationship("Company", back_populates="user", uselist=False)
    student = db.relationship("Student", back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    hr_contact = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default="Pending", nullable=False)

    user = db.relationship("User", back_populates="company")
    drives = db.relationship("Drive", back_populates="company", cascade="all, delete-orphan")


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    student_code = db.Column(db.String(30), unique=True, nullable=False)
    contact = db.Column(db.String(30), nullable=False)
    branch = db.Column(db.String(80), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    education = db.Column(db.Text, default="")
    skills = db.Column(db.Text, default="")
    experience = db.Column(db.Text, default="")
    resume_path = db.Column(db.String(250))

    user = db.relationship("User", back_populates="student")
    applications = db.relationship("Application", back_populates="student", cascade="all, delete-orphan")
    placements = db.relationship("Placement", back_populates="student")


class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    experience = db.Column(db.String(120), default="Fresher")
    salary = db.Column(db.Float, nullable=False)
    benefits = db.Column(db.Text, default="")
    eligible_branch = db.Column(db.String(80), nullable=False)
    minimum_cgpa = db.Column(db.Float, nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="Pending", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=current_time)

    company = db.relationship("Company", back_populates="drives")
    applications = db.relationship("Application", back_populates="drive", cascade="all, delete-orphan")


class Application(db.Model):
    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="unique_student_drive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("drive.id"), nullable=False)
    status = db.Column(db.String(20), default="Applied", nullable=False)
    feedback = db.Column(db.Text, default="")
    applied_at = db.Column(db.DateTime(timezone=True), default=current_time)

    student = db.relationship("Student", back_populates="applications")
    drive = db.relationship("Drive", back_populates="applications")
    interview = db.relationship("Interview", back_populates="application", uselist=False, cascade="all, delete-orphan")
    placement = db.relationship("Placement", back_populates="application", uselist=False)


class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application.id"), unique=True, nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    mode = db.Column(db.String(30), nullable=False)
    meeting_details = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.Text, default="")

    application = db.relationship("Application", back_populates="interview")


class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application.id"), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    position = db.Column(db.String(120), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    joining_date = db.Column(db.Date)
    confirmation_file = db.Column(db.String(250))

    application = db.relationship("Application", back_populates="placement")
    student = db.relationship("Student", back_populates="placements")
    company = db.relationship("Company")
