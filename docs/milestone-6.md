# Milestone 6: Application History and Status Tracking

Every application remains in history with status, feedback and interview data. Selecting a student creates one Placement record, and the student can download a simple placement confirmation. Duplicate applications are protected by API validation and `UniqueConstraint`.

Main routes: student applications, placements and confirmation download; company application status update. Tables: Application, Interview and Placement.

Viva questions: Why keep rejected applications? What is a UniqueConstraint? When is Placement created? Why use a plain-text confirmation? How is ownership checked? Answers: complete history, DB safety, selection, no unnecessary PDF dependency, and logged-in student matching.

Live changes: include joining date in confirmation; rename Selected to Placed after joining.
