#
# SQL solution stored in a Python file for this repository.
#

SOLUTION_SQL = """
WITH first_login AS (
    SELECT player_id, MIN(event_date) AS first_date
    FROM Activity
    GROUP BY player_id
)
SELECT ROUND(AVG(a.event_date IS NOT NULL), 2) AS fraction
FROM first_login f
LEFT JOIN Activity a
    ON a.player_id = f.player_id
   AND a.event_date = DATE_ADD(f.first_date, INTERVAL 1 DAY);
"""

"""
Interview explanation:
Find each player's first login, left join to an activity exactly one day later, and average the boolean match. LEFT JOIN keeps players who did not return, contributing 0. The grouping is per player; an index on (player_id, event_date) helps both phases.

Edge cases: LEFT JOIN is used whenever zero-count rows must remain; COUNT(DISTINCT ...) is used where duplicate relationships could distort the logical count.
"""
