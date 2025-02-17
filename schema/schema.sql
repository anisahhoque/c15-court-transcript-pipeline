DROP TABLE IF EXISTS argument_legislation;
DROP TABLE IF EXISTS legislation_section;
DROP TABLE IF EXISTS judgement_reference;
DROP TABLE IF EXISTS argument;
DROP TABLE IF EXISTS counsel_assignment;
DROP TABLE IF EXISTS party;
DROP TABLE IF EXISTS judge;
DROP TABLE IF EXISTS "case";
DROP TABLE IF EXISTS counsel;
DROP TABLE IF EXISTS judgment;
DROP TABLE IF EXISTS title;
DROP TABLE IF EXISTS legislation;
DROP TABLE IF EXISTS chamber;
DROP TABLE IF EXISTS court;
DROP TABLE IF EXISTS role;

CREATE TABLE role (
    role_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_name VARCHAR(10) NOT NULL
);

CREATE TABLE court (
    court_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    court_name VARCHAR(100) NOT NULL
);

CREATE TABLE chamber (
    chamber_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chamber_name VARCHAR(30) NOT NULL
);

CREATE TABLE legislation (
    legislation_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    legislation_name TEXT NOT NULL,
    link TEXT
);


CREATE TABLE judgment (
    neutral_citation VARCHAR(30) PRIMARY KEY,
    court_id INT NOT NULL,
    judgement_date DATE,
    judgment_summary TEXT NOT NULL,
    in_favour_of INT NOT NULL,
    judgment_type VARCHAR(20),
    CONSTRAINT fk_court FOREIGN KEY (court_id) REFERENCES court (court_id),
    CONSTRAINT fk_in_favour_of FOREIGN KEY (in_favour_of) REFERENCES role (role_id)
);

CREATE TABLE counsel (
    counsel_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    counsel_name VARCHAR(100) NOT NULL,
    chamber_id INT NOT NULL,
    CONSTRAINT fk_chamber FOREIGN KEY (chamber_id) REFERENCES chamber (chamber_id)
);

CREATE TABLE judge (
    judge_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    judge_name VARCHAR(50) NOT NULL,
    neutral_citation VARCHAR(30) NOT NULL,
    CONSTRAINT fk_neutral_citation FOREIGN KEY (neutral_citation) REFERENCES judgment (neutral_citation)
);

CREATE TABLE party (
    party_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    party_name VARCHAR(30) NOT NULL,
    role_id INT NOT NULL,
    neutral_citation VARCHAR(30) NOT NULL,
    CONSTRAINT neutral_citation FOREIGN KEY (neutral_citation) REFERENCES judgment(neutral_citation),
    CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES role (role_id)
);

CREATE TABLE counsel_assignment (
    counsel_assignment_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    party_id INT NOT NULL,
    counsel_id INT NOT NULL,
    CONSTRAINT fk_party FOREIGN KEY (party_id) REFERENCES party (party_id),
    CONSTRAINT fk_counsel FOREIGN KEY (counsel_id) REFERENCES counsel (counsel_id)
);

CREATE TABLE argument (
    argument_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    neutral_citation VARCHAR(30) NOT NULL,
    role_id SMALLINT NOT NULL,
    summary TEXT NOT NULL,
    CONSTRAINT fk_neutral_citation FOREIGN KEY (neutral_citation) REFERENCES judgment(neutral_citation),
    CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES role (role_id)
);

CREATE TABLE judgement_reference (
    judgement_reference_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    argument_id INT NOT NULL,
    neutral_citation VARCHAR(30) NOT NULL,
    reference VARCHAR(50),
    CONSTRAINT fk_argument FOREIGN KEY (argument_id) REFERENCES argument(argument_id)
);

CREATE TABLE legislation_section (
    legislation_section_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    section VARCHAR(10),
    legislation_id INT NOT NULL,
    CONSTRAINT fk_legislation FOREIGN KEY (legislation_id) REFERENCES legislation (legislation_id)
);

CREATE TABLE argument_legislation (
    argument_legislation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    argument_id INT NOT NULL,
    legislation_section_id BIGINT,
    CONSTRAINT fk_argument FOREIGN KEY (argument_id) REFERENCES argument (argument_id),
    CONSTRAINT fk_legislation_section FOREIGN KEY (legislation_section_id) REFERENCES legislation_section (legislation_section_id)
);
