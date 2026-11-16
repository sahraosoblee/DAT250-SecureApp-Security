INSERT INTO users (id, email, full_name, password_hash, role, phone, address, bio) VALUES
(1, 'admin@dat250.local', 'System Administrator', '$argon2id$v=19$m=65536,t=3,p=1$yNsZkVs/skmFTBgR1YNivA$kV9SZ8yPWewLAIuIBiWIHaXZRBqX7FXYwYvFvGRyN0g', 'admin', '+47 10001000', 'UiS Campus', 'Responsible for lab operations.'),
(2, 'teacher@dat250.local', 'Course Teacher', '$argon2id$v=19$m=65536,t=3,p=1$4c65vtxcX6d+BsoIkShB+w$6/TtTTpKdRwwgYgBWSK8h33oGZCoAzjemhYrgDeJq/k', 'teacher', '+47 10001001', 'UiS Campus', 'Lecturer in secure software development.'),
(3, 'ta@dat250.local', 'Teaching Assistant', '$argon2id$v=19$m=65536,t=3,p=1$HeI9Ff60cZmod+RjjSEHFA$a9WPqDAN880bwndycd988DAErAMrGzZXsLU9xAeP4Ws', 'ta', '+47 10001002', 'Stavanger', 'Supports grading and feedback.'),
(4, 'alice@student.uis.no', 'Alice Nilsen', '$argon2id$v=19$m=65536,t=3,p=1$wR5yXFcn2cl6xtPmQxe02A$nRO/VcHTRs4whStnMhVgIPOLSRA2+CZduqBonFdcrFk', 'student', '+47 40001004', 'Stavanger', 'Interested in web security.'),
(5, 'bob@student.uis.no', 'Bob Hansen', '$argon2id$v=19$m=65536,t=3,p=1$8kABAqt+QjFTofwGLyV46w$3vDGIUX/B6375PrHudTATXd3ZFUyw8L3MVnVvIlMEJ4', 'student', '+47 40001005', 'Sandnes', 'Likes backend development.'),
(6, 'charlie@student.uis.no', 'Charlie Berg', '$argon2id$v=19$m=65536,t=3,p=1$5ZtLoHtIKerv3QT+B/sWcQ$qQ0KYemVNpJBTxcdLsnOP159xTclC9ZwCqrm/tMkjBQ', 'student', '+47 40001006', 'Stavanger', 'Works on secure coding exercises.')
ON CONFLICT (id) DO NOTHING;
SELECT setval(pg_get_serial_sequence('public.users', 'id'), MAX(id))
FROM public.users;

INSERT INTO courses (id, title, description) VALUES
(1, 'DAT250 Information and Software Security', 'Core course on practical software security.'),
(2, 'DAT220 Database Systems', 'Relational design, SQL, and transactions.'),
(3, 'DAT505 Ethical Hacking', 'Applied penetration testing and legal boundaries.'),
(4, 'DAT945 Secure and Robust AI', 'Security and robustness for AI systems.')
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_groups (course_id, group_name, max_members) VALUES
(1, 'Blue Team', 4),
(1, 'Green Team', 4),
(2, 'DB Masters', 4),
(3, 'Pentest Pioneers', 4),
(4, 'AI Shield', 4);

INSERT INTO course_registrations (user_id, course_id, project_group) VALUES
(4, 1, 'Blue Team'),
(5, 1, 'Blue Team'),
(6, 1, 'Green Team'),
(4, 2, 'DB Masters'),
(5, 3, 'Pentest Pioneers');

INSERT INTO assignments (id, course_id, title, description, deadline) VALUES
(1, 1, 'Assignment 1: OWASP Testing Guide Report', 'Prepare a test plan and findings report.', NOW() + INTERVAL '7 day'),
(2, 1, 'Assignment 2: Broken Authentication and Access Control', 'Evaluate auth/session/access controls.', NOW() + INTERVAL '14 day'),
(3, 1, 'Assignment 3: Cryptography in Software', 'Analyze secrets, hashing, reset tokens.', NOW() + INTERVAL '21 day'),
(4, 1, 'Assignment 4: Secure Coding Practices', 'Patch vulnerable code and retest.', NOW() + INTERVAL '28 day')
ON CONFLICT (id) DO NOTHING;

INSERT INTO submissions (assignment_id, user_id, filename, file_path, notes) VALUES
(1, 4, 'owasp_report_alice.pdf', '4_1_owasp_report_alice.pdf', 'Initial report draft'),
(1, 5, 'owasp_report_bob.pdf', '5_1_owasp_report_bob.pdf', 'Draft'),
(2, 6, 'auth_notes_charlie.docx', '6_2_auth_notes_charlie.docx', 'Access control notes');

INSERT INTO grades (assignment_id, student_id, grader_id, grade_value, feedback, status) VALUES
(1, 4, 2, 'B+', 'Good structure, include more trace evidence.', 'published'),
(1, 5, 2, 'B', 'Solid analysis, improve remediation details.', 'published'),
(2, 6, 3, 'A-', 'Strong coverage of session handling.', 'published');

INSERT INTO messages (sender_id, recipient_id, content) VALUES
(2, 4, 'Please remember to include screenshots in your report.'),
(3, 5, 'Feedback session is available tomorrow.'),
(4, 5, 'Can we pair on Assignment 3?');

INSERT INTO course_comments (course_id, user_id, content) VALUES
(1, 4, 'The OWASP checklist is very helpful this week.'),
(1, 5, 'Can we get clarification on token handling?'),
(2, 6, 'DB isolation examples were clear.');

INSERT INTO password_reset_tokens (user_id, token) VALUES
(4, '123456'),
(5, '123456');

INSERT INTO app_settings (setting_key, setting_value) VALUES
('portal_theme', 'uis-light'),
('semester', 'Spring 2026'),
('allow_self_registration', 'true')
ON CONFLICT (setting_key) DO NOTHING;

INSERT INTO audit_logs (actor_user_id, action, details) VALUES
(1, 'seed', 'Initial seed data imported'),
(2, 'grade_publish', 'Published grades for assignment 1'),
(3, 'message_send', 'Sent onboarding messages');
