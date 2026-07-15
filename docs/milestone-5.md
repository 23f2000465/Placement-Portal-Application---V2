# Milestone 5: Student Dashboard and Applications

Students edit profiles, upload PDF resumes, search approved/open drives, see eligibility, apply once, and view status, feedback and interview details. Main routes are under `/api/student`; tables are Student, Drive, Application and Interview.

Viva questions: How is eligibility checked? Why check deadline at apply time? Why validate duplicates twice? Why restrict PDF? How does search work? Answers: branch/CGPA/year, stale pages, friendly API plus DB safety, simple safe resume type, SQL `LIKE`.

Live changes: allow comma-separated branches; add a minimum salary filter.
