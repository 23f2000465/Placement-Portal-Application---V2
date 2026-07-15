# Milestone 4: Company Dashboard and Job Management

Approved companies can edit profiles, create/update/delete drives, see applicants, update status/feedback and schedule interviews. Pending companies receive HTTP 403 on drive creation.

Main routes are under `/api/company`. Tables: Company, Drive, Application, Student and Interview. Test with the standard unittest command and run both servers.

Viva questions: Why check drive ownership? Why 403 for pending companies? Why one interview per application? Why prevent deleting a drive with applications? What does PATCH do? Answers: data security, approval rule, simple schema, history safety, and partial update.

Live changes: allow another status; add interview notes input.
