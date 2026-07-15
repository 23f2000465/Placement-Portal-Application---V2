# Quick Viva Guide

## Project flow

1. Admin is created by `init_db.py` and logs in.
2. Student and company register through Vue forms and Flask APIs.
3. Admin approves the company.
4. Company creates a drive; admin approves it.
5. Eligible student applies once.
6. Company shortlists, schedules interview, adds feedback and selects the student.
7. Student sees full history and downloads placement confirmation or async CSV.

## Core concepts in simple words

- **Blueprint:** related routes ka group, jaise all admin routes.
- **Route:** URL ko Python function se connect karta hai.
- **GET/POST/PATCH:** read/create/partly update.
- **ForeignKey:** do tables ko ID se connect karta hai.
- **Session:** signed cookie se logged-in user ID yaad rakhti hai.
- **RBAC:** role ke basis par API access allow karta hai.
- **Redis cache:** frequently read JSON ka temporary fast copy.
- **Celery worker:** background task execute karta hai.
- **Celery Beat:** fixed time par task queue mein bhejta hai.
- **Broker:** Redis worker tak task message pahunchata hai.

## Common viva checks

- Pending company drive create kare: backend returns 403.
- Ineligible student apply kare: backend returns 400 with reason.
- Duplicate application: API returns 409 and database has a unique constraint.
- Wrong role calls API: role decorator returns 403.
- Redis stops: cache helper catches error and SQLite response still works.

## Easy live modifications

1. Change cache expiry in `backend/config.py`.
2. Add a field to a JSON response.
3. Add another allowed application status.
4. Add location to a search filter.
5. Change Celery Beat reminder time in `backend/tasks.py`.
