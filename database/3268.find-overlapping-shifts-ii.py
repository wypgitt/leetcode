#
# @lc app=leetcode id=3268 lang=python3
#
# [3268] Find Overlapping Shifts II
#
# https://leetcode.com/problems/find-overlapping-shifts-ii/description/
#
# database
# Hard (55.64%)
# Likes:    8
# Dislikes: 7
# Total Accepted:    1.4K
# Total Submissions: 2.5K
# Testcase Example:  "{\"headers\": {\"EmployeeShifts\":[\"employee_id\",\"start_time\",\"end_time\"]},\"rows\":{\"EmployeeShifts\":[[1,\"2023-10-01 09:00:00\",\"2023-10-01 17:00:00\"],[1,\"2023-10-01 15:00:00\",\"2023-10-01 23:00:00\"],[1,\"2023-10-01 16:00:00\",\"2023-10-02 00:00:00\"],[2,\"2023-10-01 09:00:00\",\"2023-10-01 17:00:00\"],[2,\"2023-10-01 11:00:00\",\"2023-10-01 19:00:00\"],[3,\"2023-10-01 09:00:00\",\"2023-10-01 17:00:00\"]]}}"
#
#
# Table: EmployeeShifts
#
# +------------------+----------+
# | Column Name      | Type     |
# +------------------+----------+
# | employee_id      | int      |
# | start_time       | datetime |
# | end_time         | datetime |
# +------------------+----------+
# (employee_id, start_time) is the unique key for this table.
# This table contains information about the shifts worked by employees,
# including the start time, and end time.
#
# Write a solution to analyze overlapping shifts for each employee. Two
# shifts are considered overlapping if they occur on the same date and one
# shift's end_time is later than another shift's start_time.
#
# For each employee, calculate the following:
#
# The maximum number of shifts that overlap at any given time.
#
# The total duration of all overlaps in minutes.
#
# Return the result table ordered by employee_id in ascending order.
#
# The query result format is in the following example.
#
# Example:
#
# Input:
#
# EmployeeShifts table:
#
# +-------------+---------------------+---------------------+
# | employee_id | start_time          | end_time            |
# +-------------+---------------------+---------------------+
# | 1           | 2023-10-01 09:00:00 | 2023-10-01 17:00:00 |
# | 1           | 2023-10-01 15:00:00 | 2023-10-01 23:00:00 |
# | 1           | 2023-10-01 16:00:00 | 2023-10-02 00:00:00 |
# | 2           | 2023-10-01 09:00:00 | 2023-10-01 17:00:00 |
# | 2           | 2023-10-01 11:00:00 | 2023-10-01 19:00:00 |
# | 3           | 2023-10-01 09:00:00 | 2023-10-01 17:00:00 |
# +-------------+---------------------+---------------------+
#
# Output:
#
# +-------------+---------------------------+------------------------+
# | employee_id | max_overlapping_shifts    | total_overlap_duration |
# +-------------+---------------------------+------------------------+
# | 1           | 3                         | 600                    |
# | 2           | 2                         | 360                    |
# | 3           | 1                         | 0                      |
# +-------------+---------------------------+------------------------+
#
# Explanation:
#
# Employee 1 has 3 shifts:
#
# 2023-10-01 09:00:00 to 2023-10-01 17:00:00
#
# 2023-10-01 15:00:00 to 2023-10-01 23:00:00
#
# 2023-10-01 16:00:00 to 2023-10-02 00:00:00
#
#         The maximum number of overlapping shifts is 3 (from 16:00 to
# 17:00). The total overlap duration is: - 2 hours (15:00-17:00) between
# 1st and 2nd shifts - 1 hour (16:00-17:00) between 1st and 3rd shifts - 7
# hours (16:00-23:00) between 2nd and 3rd shifts Total: 10 hours = 600
# minutes
#
# Employee 2 has 2 shifts:
#
# 2023-10-01 09:00:00 to 2023-10-01 17:00:00
#
# 2023-10-01 11:00:00 to 2023-10-01 19:00:00
#
#         The maximum number of overlapping shifts is 2. The total overlap
# duration is 6 hours (11:00-17:00) = 360 minutes.
#
# Employee 3 has only 1 shift, so there are no overlaps.
#
# The output table contains the employee_id, the maximum number of
# simultaneous overlaps, and the total overlap duration in minutes for
# each employee, ordered by employee_id in ascending order.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: per employee, max simultaneous overlapping shifts and total
        pairwise overlap duration in minutes. Include employees with a single
        shift (max=1, duration=0). Order by employee_id ASC.

        Algorithm:
        - Expand each shift into +1 at start_time and -1 at end_time; window over
          ordered events computing running concurrency.
        - max_overlapping_shifts = MAX(concurrency) (treating starts before ends
          at equal timestamps carefully via ordering).
        - total_overlap_duration = Σ C(c,2) * minutes between consecutive events
          (pairwise overlap measure).
        - UNION employees so isolates appear with 0 duration.

        Complexity: O(N log N) per employee with event sort.
        """
        self.sql = """
WITH events AS (
  SELECT employee_id, start_time AS ts, 1 AS delta
  FROM EmployeeShifts
  UNION ALL
  SELECT employee_id, end_time AS ts, -1 AS delta
  FROM EmployeeShifts
),
ordered AS (
  SELECT
    employee_id,
    ts,
    delta,
    SUM(delta) OVER (
      PARTITION BY employee_id
      ORDER BY ts ASC, delta ASC
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS concurrent
  FROM events
),
spans AS (
  SELECT
    employee_id,
    ts,
    concurrent,
    LEAD(ts) OVER (PARTITION BY employee_id ORDER BY ts ASC, delta ASC) AS next_ts,
    delta
  FROM ordered
),
agg AS (
  SELECT
    employee_id,
    MAX(concurrent) AS max_overlapping_shifts,
    COALESCE(
      SUM(
        CASE
          WHEN next_ts IS NOT NULL AND concurrent >= 2
          THEN concurrent * (concurrent - 1) / 2
               * TIMESTAMPDIFF(MINUTE, ts, next_ts)
          ELSE 0
        END
      ),
      0
    ) AS total_overlap_duration
  FROM spans
  GROUP BY employee_id
)
SELECT employee_id, max_overlapping_shifts, total_overlap_duration
FROM agg
ORDER BY employee_id;
"""
        return self.sql
# @lc code=end
