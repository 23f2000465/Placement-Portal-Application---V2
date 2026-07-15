# Milestone 1: Database Models and Schema

## What it implements

SQLite tables for users, companies, students, drives, applications, interviews and placements. The admin is created programmatically and duplicate applications are blocked by the database.

## Main files

- `backend/models.py`: tables and relationships
- `backend/init_db.py`: creates tables and one admin
- `backend/tests/test_models.py`: model tests

## How to run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

## How to test

```bash
cd backend
python -m unittest discover -s tests
```

## Simple concepts

- **ForeignKey:** doosre table ke record ko ID se connect karta hai.
- **relationship:** connected Python objects ko easily access karne deta hai.
- **back_populates:** relation ko dono sides se available rakhta hai.
- **UniqueConstraint:** same student ko same drive mein dobara apply karne se database level par rokta hai.

## Five viva questions

1. **Why SQLite?** It is required, simple and stored in one local file.
2. **Why hash passwords?** A leaked database should not reveal actual passwords.
3. **What is an ORM?** It maps Python classes to database tables.
4. **Why a unified User table?** Login details stay in one place and `role` identifies access.
5. **How are duplicate applications prevented?** API validation later, plus a database unique constraint now.

## Possible live-code changes

1. Add a `phone` field to Company and recreate the test database.
2. Change a new drive's default status from `Pending` to `Closed`.
