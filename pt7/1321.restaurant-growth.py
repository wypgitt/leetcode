"""
LeetCode 1321 - Restaurant Growth

The file in this repo has a `.py` extension, so the SQL answer is stored as a
string to keep the file valid Python. Copy the contents of `QUERY` into the
LeetCode MySQL editor.
"""

QUERY = """
WITH daily AS (
    SELECT
        visited_on,
        SUM(amount) AS amount
    FROM Customer
    GROUP BY visited_on
)
SELECT
    current_day.visited_on,
    SUM(window_day.amount) AS amount,
    ROUND(SUM(window_day.amount) / 7, 2) AS average_amount
FROM daily AS current_day
JOIN daily AS window_day
    ON window_day.visited_on BETWEEN DATE_SUB(current_day.visited_on, INTERVAL 6 DAY)
                                AND current_day.visited_on
WHERE current_day.visited_on >= (
    SELECT DATE_ADD(MIN(visited_on), INTERVAL 6 DAY)
    FROM daily
)
GROUP BY current_day.visited_on
ORDER BY current_day.visited_on;
"""

#
# Interview explanation
# ---------------------
# Idea:
# Multiple customers can visit on the same date, so first collapse the table to
# one row per day. Then, for each possible output day, join the daily table to
# the seven-calendar-day window ending on that day.
#
# Why this query:
# - The `daily` CTE removes duplicate dates by summing `amount`.
# - The self-join selects days from `current_day - 6` through `current_day`.
# - The `WHERE` clause skips the first six dates because a full seven-day
#   report cannot end before then.
# - `ROUND(SUM(...) / 7, 2)` computes the required seven-day average.
#
# Data structure:
# In SQL terms, `daily` is the intermediate table. The self-join materializes
# the rolling window for each output date.
#
# Edge cases:
# - Several customers on the same date: handled by `GROUP BY visited_on`.
# - First six dates: excluded.
# - Exact cents/decimals: `ROUND(..., 2)` matches the requested precision.
#
# Complexity:
# - Let d be the number of distinct dates. A straightforward self-join is
#   roughly O(d * 7) when the date condition can use an index, though database
#   plans vary.
# - Space depends on the database execution plan for the CTE and join.
#
# Improvement:
# On MySQL 8 with guaranteed consecutive dates, a window function over the
# daily table can express this more compactly. The self-join version follows
# calendar dates explicitly, which is safer to explain in interviews.
