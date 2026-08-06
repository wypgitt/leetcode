#
# SQL solution stored in a Python file for this repository.
#

SOLUTION_SQL = """
SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM Insurance
WHERE tiv_2015 IN (
    SELECT tiv_2015
    FROM Insurance
    GROUP BY tiv_2015
    HAVING COUNT(*) > 1
)
AND (lat, lon) IN (
    SELECT lat, lon
    FROM Insurance
    GROUP BY lat, lon
    HAVING COUNT(*) = 1
);
"""

"""
Interview explanation:
Keep policies whose 2015 investment value is shared by at least one other policy, while their location pair is unique. The two grouped subqueries express those two independent filters. Sum tiv_2016 and round to two decimals.

Edge cases: LEFT JOIN is used whenever zero-count rows must remain; COUNT(DISTINCT ...) is used where duplicate relationships could distort the logical count.
"""
