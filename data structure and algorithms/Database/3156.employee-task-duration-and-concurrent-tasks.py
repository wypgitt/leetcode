#
# @lc app=leetcode id=3156 lang=python3
#
# [3156] Employee Task Duration and Concurrent Tasks
#
# https://leetcode.com/problems/employee-task-duration-and-concurrent-tasks/description/
#
# database
# Hard (39.50%)
# Likes:    13
# Dislikes: 3
# Total Accepted:    1.8K
# Total Submissions: 4.5K
# Testcase Example:  "{\"headers\":{\"Tasks\":[\"task_id\",\"employee_id\",\"start_time\",\"end_time\"]},\"rows\":{\"Tasks\":[[1,1001,\"2023-05-01 08:00:00\",\"2023-05-01 09:00:00\"],[2,1001,\"2023-05-01 08:30:00\",\"2023-05-01 10:30:00\"],[3,1001,\"2023-05-01 11:00:00\",\"2023-05-01 12:00:00\"],[7,1001,\"2023-05-01 13:00:00\",\"2023-05-01 15:30:00\"],[4,1002,\"2023-05-01 09:00:00\",\"2023-05-01 10:00:00\"],[5,1002,\"2023-05-01 09:30:00\",\"2023-05-01 11:30:00\"],[6,1003,\"2023-05-01 14:00:00\",\"2023-05-01 16:00:00\"]]}}"
#
#
# Table: Tasks
#
# +---------------+----------+
# | Column Name   | Type     |
# +---------------+----------+
# | task_id       | int      |
# | employee_id   | int      |
# | start_time    | datetime |
# | end_time      | datetime |
# +---------------+----------+
# (task_id, employee_id) is the primary key for this table.
# Each row in this table contains the task identifier, the employee
# identifier, and the start and end times of each task.
#
# Write a solution to find the total duration of tasks for each employee
# and the maximum number of concurrent tasks an employee handled at any
# point in time. The total duration should be rounded down to the nearest
# number of full hours.
#
# Return the result table ordered by employee_id ascending order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# Tasks table:
#
# +---------+-------------+---------------------+---------------------+
# | task_id | employee_id | start_time          | end_time            |
# +---------+-------------+---------------------+---------------------+
# | 1       | 1001        | 2023-05-01 08:00:00 | 2023-05-01 09:00:00 |
# | 2       | 1001        | 2023-05-01 08:30:00 | 2023-05-01 10:30:00 |
# | 3       | 1001        | 2023-05-01 11:00:00 | 2023-05-01 12:00:00 |
# | 7       | 1001        | 2023-05-01 13:00:00 | 2023-05-01 15:30:00 |
# | 4       | 1002        | 2023-05-01 09:00:00 | 2023-05-01 10:00:00 |
# | 5       | 1002        | 2023-05-01 09:30:00 | 2023-05-01 11:30:00 |
# | 6       | 1003        | 2023-05-01 14:00:00 | 2023-05-01 16:00:00 |
# +---------+-------------+---------------------+---------------------+
#
# Output:
#
# +-------------+------------------+----------------------+
# | employee_id | total_task_hours | max_concurrent_tasks |
# +-------------+------------------+----------------------+
# | 1001        | 6                | 2                    |
# | 1002        | 2                | 2                    |
# | 1003        | 2                | 1                    |
# +-------------+------------------+----------------------+
#
# Explanation:
#
# For employee ID 1001:
#
# Task 1 and Task 2 overlap from 08:30 to 09:00 (30 minutes).
#
# Task 7 has a duration of 150 minutes (2 hours and 30 minutes).
#
# Total task time: 60 (Task 1) + 120 (Task 2) + 60 (Task 3) + 150 (Task 7)
# - 30 (overlap) = 360 minutes = 6 hours.
#
# Maximum concurrent tasks: 2 (during the overlap period).
#
# For employee ID 1002:
#
# Task 4 and Task 5 overlap from 09:30 to 10:00 (30 minutes).
#
# Total task time: 60 (Task 4) + 120 (Task 5) - 30 (overlap) = 150 minutes
# = 2 hours and 30 minutes.
#
# Total task hours (rounded down): 2 hours.
#
# Maximum concurrent tasks: 2 (during the overlap period).
#
# For employee ID 1003:
#
# No overlapping tasks.
#
# Total task time: 120 minutes = 2 hours.
#
# Maximum concurrent tasks: 1.
#
# Note: Output table is ordered by employee_id in ascending order.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Tasks(task_id, employee_id, start_time, end_time).
        Per employee: union duration of tasks floored to whole hours, and max
        concurrent tasks. Order by employee_id ASC.

        Algorithm:
        - Merge intervals via running MAX(prev end) window to get union length.
        - Sweep +1 at start / -1 at end for max concurrency (ends before starts).
        - FLOOR(union_seconds / 3600); join the two aggregates.

        Complexity: O(N log N) with sorts from window/order.
        """
        self.sql = """
WITH ordered AS (
    SELECT
        employee_id,
        start_time,
        end_time,
        MAX(end_time) OVER (
            PARTITION BY employee_id
            ORDER BY start_time, end_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prev_max_end
    FROM Tasks
),
flagged AS (
    SELECT
        employee_id,
        start_time,
        end_time,
        CASE
            WHEN prev_max_end IS NULL OR start_time > prev_max_end THEN 1
            ELSE 0
        END AS is_new
    FROM ordered
),
grouped AS (
    SELECT
        employee_id,
        start_time,
        end_time,
        SUM(is_new) OVER (
            PARTITION BY employee_id
            ORDER BY start_time, end_time
        ) AS grp
    FROM flagged
),
merged AS (
    SELECT
        employee_id,
        MIN(start_time) AS st,
        MAX(end_time) AS en
    FROM grouped
    GROUP BY employee_id, grp
),
hours AS (
    SELECT
        employee_id,
        FLOOR(SUM(TIMESTAMPDIFF(SECOND, st, en)) / 3600) AS total_task_hours
    FROM merged
    GROUP BY employee_id
),
events AS (
    SELECT employee_id, start_time AS t, 1 AS delta FROM Tasks
    UNION ALL
    SELECT employee_id, end_time AS t, -1 AS delta FROM Tasks
),
running AS (
    SELECT
        employee_id,
        SUM(delta) OVER (
            PARTITION BY employee_id
            ORDER BY t ASC, delta ASC
            ROWS UNBOUNDED PRECEDING
        ) AS concurrent
    FROM events
),
conc AS (
    SELECT employee_id, MAX(concurrent) AS max_concurrent_tasks
    FROM running
    GROUP BY employee_id
)
SELECT
    h.employee_id,
    h.total_task_hours,
    c.max_concurrent_tasks
FROM hours h
JOIN conc c ON h.employee_id = c.employee_id
ORDER BY h.employee_id;
"""
        return self.sql
# @lc code=end
