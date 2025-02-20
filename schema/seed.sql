-- Insert courts
INSERT INTO court (court_name) VALUES 
('Supreme Court'),
('Court of Appeal'),
('High Court');

-- Insert chambers
INSERT INTO chamber (chamber_name) VALUES 
('Blackstone Chambers'),
('Fountain Court Chambers'),
('Brick Court Chambers');

-- Insert counsel
INSERT INTO counsel (counsel_name, chamber_id) VALUES 
('John Smith', 1),
('Jane Doe', 2),
('Robert Brown', 3),
('Emily White', 1),
('Michael Green', 2);

-- Insert roles
INSERT INTO role (role_name) VALUES 
('Claimant'),
('Defendant');

-- Insert judgments
INSERT INTO judgment (neutral_citation, court_id, judgment_date, judgment_summary, in_favour_of, judgment_type_id, judge_name) VALUES 
('2025-SC-001', 1, '2025-01-10', 'Case involving contract dispute.', 1, 2, 'Justice A. Roberts'),
('2025-CA-002', 2, '2025-01-15', 'Criminal fraud case.', 2, 1, 'Justice B. Johnson'),
('2025-HC-003', 3, '2025-01-20', 'Employment dispute.', 1, 2, 'Justice C. Smith');

-- Insert parties with multiple claimants and defendants in some cases
INSERT INTO party (party_name, role_id, neutral_citation) VALUES 
-- Judgment 1 (2025-SC-001) has 2 claimants and 1 defendant
('Alice Johnson', 1, '2025-SC-001'),
('Bob Richards', 1, '2025-SC-001'),
('XYZ Corporation', 2, '2025-SC-001'),

-- Judgment 2 (2025-CA-002) has 1 claimant and 2 defendants
('State Prosecutor', 1, '2025-CA-002'),
('John Doe', 2, '2025-CA-002'),
('Jane Roe', 2, '2025-CA-002'),

-- Judgment 3 (2025-HC-003) has 2 claimants and 2 defendants
('Michael Thomas', 1, '2025-HC-003'),
('Sarah Evans', 1, '2025-HC-003'),
('ABC Ltd.', 2, '2025-HC-003'),
('DEF Inc.', 2, '2025-HC-003');

-- Assign counsel to parties
INSERT INTO counsel_assignment (party_id, counsel_id) VALUES 
(1, 1),  -- Alice Johnson represented by John Smith
(2, 2),  -- Bob Richards represented by Jane Doe
(3, 3),  -- XYZ Corporation represented by Robert Brown
(4, 4),  -- State Prosecutor represented by Emily White
(5, 5),  -- John Doe represented by Michael Green
(6, 1),  -- Jane Roe represented by John Smith
(7, 2),  -- Michael Thomas represented by Jane Doe
(8, 3),  -- Sarah Evans represented by Robert Brown
(9, 4),  -- ABC Ltd. represented by Emily White
(10, 5); -- DEF Inc. represented by Michael Green