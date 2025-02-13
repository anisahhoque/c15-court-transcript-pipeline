-- Step 1: Insert into base tables that don’t depend on other data
INSERT INTO role (role_name) VALUES 
('Plaintiff'), ('Defendant');

INSERT INTO court (court_name) VALUES 
('Supreme Court'), ('High Court');

INSERT INTO chamber (chamber_name) VALUES 
('Chamber A'), ('Chamber B');

INSERT INTO legislation (legislation_name, link) VALUES 
('Legislation 1', 'https://example.com/legislation1'), 
('Legislation 2', 'https://example.com/legislation2');

INSERT INTO title (title_name) VALUES 
('Mr'), ('Dr');

-- Step 2: Insert into judgment and case tables
INSERT INTO judgment (neutral_citation, court_id, hearing_date, judgement_date) 
VALUES 
('2025/01', 1, '2025-01-01', '2025-02-01');

INSERT INTO "case" (case_number, neutral_citation) 
VALUES 
('A123', '2025/01');

-- Step 3: Insert into other tables that depend on the above
INSERT INTO judge (judge_name, title_id, neutral_citation) 
VALUES 
('Judge John Doe', 1, '2025/01');

INSERT INTO party (party_name, case_id, role_id) 
VALUES 
('Party A', 1, 1), 
('Party B', 1, 2);

-- Step 4: Insert into counsel and counsel_assignment tables
INSERT INTO counsel (court_name, chamber_id) 
VALUES 
('Counsel A', 1), 
('Counsel B', 2);

INSERT INTO counsel_assignment (party_id, counsel_id) 
VALUES 
(1, 1), 
(2, 2);

-- Step 5: Insert into argument and related tables
INSERT INTO argument (neutral_citation, role_id, summary, counsel_id) 
VALUES 
('2025/01', 1, 'Argument A summary', 1), 
('2025/01', 2, 'Argument B summary', 2);

INSERT INTO judgement_reference (argument_id, neutral_citation, reference) 
VALUES 
(1, '2025/01', 'Reference 1'), 
(2, '2025/01', 'Reference 2');

-- Step 6: Insert into legislation_section and argument_legislation tables
INSERT INTO legislation_section (section, legislation_id) 
VALUES 
('Section 1', 1), 
('Section 2', 2);

INSERT INTO argument_legislation (argument_id, legislation_section_id) 
VALUES 
(1, 1), 
(2, 2);
