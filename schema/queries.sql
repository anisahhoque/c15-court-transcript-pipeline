SELECT j.neutral_citation AS judgment, jd.judge_name AS judge, court_name as court
FROM judgment j
JOIN judge jd
ON j.neutral_citation = jd.neutral_citation
JOIN court c
ON j.court_id = c.court_id;
