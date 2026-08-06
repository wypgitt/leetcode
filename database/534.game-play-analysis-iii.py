#
# SQL solution stored in a Python file for this repository.
#

SOLUTION_SQL = """
SELECT
    player_id,
    event_date,
    SUM(games_played) OVER (
        PARTITION BY player_id
        ORDER BY event_date
    ) AS games_played_so_far
FROM Activity;
"""

"""
Interview explanation:
Use a window running sum partitioned by player and ordered by event_date. This keeps one output row per original activity row and accumulates games through that date. Time is driven by the database sort on (player_id, event_date); indexing those columns is the main improvement.

Edge cases: LEFT JOIN is used whenever zero-count rows must remain; COUNT(DISTINCT ...) is used where duplicate relationships could distort the logical count.
"""
