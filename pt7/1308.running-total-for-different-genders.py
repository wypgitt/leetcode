"""
LeetCode 1308 - Running Total for Different Genders

The file in this repo has a `.py` extension, so the SQL answer is stored as a
string to keep the file valid Python. Copy the contents of `QUERY` into the
LeetCode MySQL editor.
"""

QUERY = """
SELECT
    gender,
    day,
    SUM(score) OVER (
        PARTITION BY gender
        ORDER BY day
    ) AS total
FROM Scores
ORDER BY gender, day;
"""

#
# Interview explanation
# ---------------------
# Idea:
# For each gender, we need a cumulative score ordered by day. This is exactly
# what a SQL window aggregate does: it keeps the original rows while computing
# a running SUM over an ordered partition.
#
# Why this query:
# - `PARTITION BY gender` starts an independent running total for each gender.
# - `ORDER BY day` defines chronological order inside that gender.
# - `SUM(score) OVER (...)` returns the cumulative total through the current
#   row.
# - Final `ORDER BY gender, day` matches the requested output order.
#
# Data structure:
# Conceptually, the database groups rows into per-gender ordered streams. The
# window function scans each stream and carries the running sum.
#
# Edge cases:
# - The first row for a gender simply has total equal to its own score.
# - Genders with different numbers of days are handled independently.
# - Equal scores or zero scores do not need special handling.
#
# Complexity:
# - Time: O(n log n) in a typical database plan because rows must be ordered by
#   `(gender, day)`.
# - Space: depends on the database sort/window implementation.
#
# Tests to discuss:
# Given rows like F day 1 score 17, F day 2 score 23, M day 1 score 7, the
# totals are F: 17, 40 and M: 7, because partitions do not mix.
