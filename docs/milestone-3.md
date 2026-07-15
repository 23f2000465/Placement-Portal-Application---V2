# Milestone 3: Admin Dashboard and Management

Admin can view counts, search companies/students, approve or reject companies/drives, inspect applications and activate/deactivate accounts. Routes are under `/api/admin`; all require the Admin role.

Tables involved: User, Company, Student, Drive and Application. Run the normal backend and frontend commands; test with `python -m unittest discover -s tests`.

Viva questions: What is RBAC? Why return 403? How does search work? Why can admin not deactivate itself? Why are approvals stored as status text? Simple answers: role checking, forbidden access, SQL `LIKE`, safety, and readable state.

Live changes: add location to company search; add a Pending-only filter.
