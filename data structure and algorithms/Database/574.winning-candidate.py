#
# SQL solution stored in a Python file for this repository.
#

SOLUTION_SQL = """
SELECT c.name
FROM Candidate c
JOIN Vote v ON v.candidateId = c.id
GROUP BY c.id, c.name
ORDER BY COUNT(*) DESC
LIMIT 1;
"""

"""
Interview explanation:
Join votes to candidates, group by candidate, and choose the group with the largest vote count. The problem guarantees a winner, so LIMIT 1 is sufficient. If ties were possible, use RANK instead.

Edge cases: LEFT JOIN is used whenever zero-count rows must remain; COUNT(DISTINCT ...) is used where duplicate relationships could distort the logical count.
"""
