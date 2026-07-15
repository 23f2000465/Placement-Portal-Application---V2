# Milestone 7: Celery Jobs and CSV Export

Redis is the message broker. A Celery worker executes tasks, Celery Beat sends scheduled tasks, and a task is one background function. Daily reminders cover deadlines/interviews; the monthly HTML report is created on day one; students trigger application CSV exports.

Run Redis, then `celery -A tasks.celery worker --loglevel=info` and `celery -A tasks.celery beat --loglevel=info` from `backend`. Without SMTP settings, emails are saved in ignored `backend/reports` for an easy local demo.

Routes: `POST /api/student/exports`, status and download GET routes. Tables: ExportJob plus application-related tables.

Viva questions: What is Redis? Broker? Worker? Beat? Task? Answers: in-memory queue, message carrier, executor, scheduler, background function.

Live changes: change reminder time; add salary to CSV.
