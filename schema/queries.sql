SELECT j.neutral_citation AS judgment, jd.judge_name AS judge, court_name as court
FROM judgment j
JOIN judge jd
ON j.neutral_citation = jd.neutral_citation
JOIN court c
ON j.court_id = c.court_id;

SELECT 
    j.neutral_citation, 
    j.court_id, 
    j.hearing_date, 
    j.judgement_date, 
    a.argument_id, 
    a.summary AS argument_summary
FROM 
    judgment j
JOIN 
    argument a ON j.neutral_citation = a.neutral_citation
ORDER BY 
    j.judgement_date DESC
LIMIT 1;
