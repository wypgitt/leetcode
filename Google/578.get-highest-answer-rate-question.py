#
# SQL solution stored in a Python file for this repository.
#

SOLUTION_SQL = """
SELECT question_id AS survey_log
FROM SurveyLog
GROUP BY question_id
ORDER BY SUM(action = 'answer') / SUM(action = 'show') DESC, question_id
LIMIT 1;
"""

"""
Interview explanation:
Answer rate is answers divided by shows for each question. Boolean expressions aggregate as 1/0 in MySQL. Ordering by question_id after the rate gives deterministic behavior if rates tie.

Edge cases: LEFT JOIN is used whenever zero-count rows must remain; COUNT(DISTINCT ...) is used where duplicate relationships could distort the logical count.
"""
