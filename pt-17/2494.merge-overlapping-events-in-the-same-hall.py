#
# @lc app=leetcode id=2494 lang=python3
#
# [2494] Merge Overlapping Events in the Same Hall
#
# https://leetcode.com/problems/merge-overlapping-events-in-the-same-hall/description/
#
# database
# Hard (37.88%)
# Likes:    56
# Dislikes: 8
# Total Accepted:    3.3K
# Total Submissions: 8.8K
# Testcase Example:  "{\"headers\": {\"HallEvents\": [\"hall_id\", \"start_day\", \"end_day\"]}, \"rows\": {\"HallEvents\": [[1, \"2023-01-13\", \"2023-01-14\"], [1, \"2023-01-14\", \"2023-01-17\"], [1, \"2023-01-18\", \"2023-01-25\"], [2, \"2022-12-09\", \"2022-12-23\"], [2, \"2022-12-13\", \"2022-12-17\"], [3, \"2022-12-01\", \"2023-01-30\"]]}}"
#
#
# Table: HallEvents
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | hall_id     | int  |
# | start_day   | date |
# | end_day     | date |
# +-------------+------+
# This table may contain duplicates rows.
# Each row of this table indicates the start day and end day of an event
# and the hall in which the event is held.
#
# Write a solution to merge all the overlapping events that are held in
# the same hall. Two events overlap if they have at least one day in
# common.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# HallEvents table:
# +---------+------------+------------+
# | hall_id | start_day  | end_day    |
# +---------+------------+------------+
# | 1       | 2023-01-13 | 2023-01-14 |
# | 1       | 2023-01-14 | 2023-01-17 |
# | 1       | 2023-01-18 | 2023-01-25 |
# | 2       | 2022-12-09 | 2022-12-23 |
# | 2       | 2022-12-13 | 2022-12-17 |
# | 3       | 2022-12-01 | 2023-01-30 |
# +---------+------------+------------+
# Output:
# +---------+------------+------------+
# | hall_id | start_day  | end_day    |
# +---------+------------+------------+
# | 1       | 2023-01-13 | 2023-01-17 |
# | 1       | 2023-01-18 | 2023-01-25 |
# | 2       | 2022-12-09 | 2022-12-23 |
# | 3       | 2022-12-01 | 2023-01-30 |
# +---------+------------+------------+
# Explanation: There are three halls.
# Hall 1:
# - The two events ["2023-01-13", "2023-01-14"] and ["2023-01-14",
# "2023-01-17"] overlap. We merge them in one event ["2023-01-13",
# "2023-01-17"].
# - The event ["2023-01-18", "2023-01-25"] does not overlap with any other
# event, so we leave it as it is.
# Hall 2:
# - The two events ["2022-12-09", "2022-12-23"] and ["2022-12-13",
# "2022-12-17"] overlap. We merge them in one event ["2022-12-09",
# "2022-12-23"].
# Hall 3:
# - The hall has only one event, so we return it. Note that we only
# consider the events of each hall separately.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. HallEvents(hall_id, start_day, end_day). Merge overlapping
        events within the same hall (share at least one day).

        Algorithm:
        - Per hall order by start; running max end; mark new group when
          start > prev running max; aggregate min start / max end per group.

        Complexity: O(N log N) with windows.
        """
        self.sql = """
WITH
  S AS (
    SELECT
      hall_id,
      start_day,
      end_day,
      MAX(end_day) OVER (
        PARTITION BY hall_id
        ORDER BY start_day, end_day
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      ) AS cur_max_end_day
    FROM HallEvents
  ),
  T AS (
    SELECT
      *,
      IF(
        start_day <= LAG(cur_max_end_day) OVER (
          PARTITION BY hall_id
          ORDER BY start_day, end_day
        ),
        0,
        1
      ) AS start
    FROM S
  ),
  P AS (
    SELECT
      *,
      SUM(start) OVER (
        PARTITION BY hall_id
        ORDER BY start_day, end_day
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      ) AS gid
    FROM T
  )
SELECT hall_id, MIN(start_day) AS start_day, MAX(end_day) AS end_day
FROM P
GROUP BY hall_id, gid;
"""
        return self.sql
# @lc code=end

