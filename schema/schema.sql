\c judgments
DROP TABLE IF EXISTS counsel_assignment;
DROP TABLE IF EXISTS party;
DROP TABLE IF EXISTS counsel;
DROP TABLE IF EXISTS judgment;
DROP TABLE IF EXISTS court;
DROP TABLE IF EXISTS judgment_type;
DROP TABLE IF EXISTS chamber;
DROP TABLE IF EXISTS role;


CREATE TABLE role (
    role_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    role_name VARCHAR(10) NOT NULL
);


CREATE TABLE court (
    court_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    court_name VARCHAR(100) NOT NULL
);


CREATE TABLE judgment_type (
    judgment_type_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    judgment_type VARCHAR(30)
);

CREATE TABLE chamber (
    chamber_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chamber_name VARCHAR(50) NOT NULL
);

CREATE TABLE counsel (
    counsel_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    counsel_name VARCHAR(100) NOT NULL,
    chamber_id SMALLINT,
    CONSTRAINT fk_chamber FOREIGN KEY (chamber_id) REFERENCES chamber (chamber_id)
);

CREATE TABLE judgment (
    neutral_citation VARCHAR(30) PRIMARY KEY,
    court_id INT NOT NULL,
    judgment_date DATE,
    judgment_summary TEXT NOT NULL,
    in_favour_of INT NOT NULL,
    judgment_type_id SMALLINT,
    judge_name VARCHAR(100) NOT NULL,
    CONSTRAINT fk_in_favour_of FOREIGN KEY (in_favour_of) REFERENCES role (role_id),
    CONSTRAINT fk_court FOREIGN KEY (court_id) REFERENCES court (court_id),
    CONSTRAINT fk_judgment_type FOREIGN KEY (judgment_type_id) REFERENCES judgment_type(judgment_type_id)
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
