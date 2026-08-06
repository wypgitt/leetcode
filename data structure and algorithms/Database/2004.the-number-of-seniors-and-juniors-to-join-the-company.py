#
# @lc app=leetcode id=2004 lang=python3
#
# [2004] The Number of Seniors and Juniors to Join the Company
#
# https://leetcode.com/problems/the-number-of-seniors-and-juniors-to-join-the-company/description/
#
# database
# Hard (46.44%)
# Likes:    119
# Dislikes: 15
# Total Accepted:    11.2K
# Total Submissions: 24.1K
# Testcase Example:  "{\"headers\":{\"Candidates\":[\"employee_id\",\"experience\",\"salary\"]},\"rows\":{\"Candidates\":[[1,\"Junior\",10000],[9,\"Junior\",10000],[2,\"Senior\",20000],[11,\"Senior\",20000],[13,\"Senior\",50000],[4,\"Junior\",40000]]}}"
#
#
# Table: Candidates
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | employee_id | int  |
# | experience  | enum |
# | salary      | int  |
# +-------------+------+
# employee_id is the column with unique values for this table.
# experience is an ENUM (category) type of values ('Senior', 'Junior').
# Each row of this table indicates the id of a candidate, their monthly
# salary, and their experience.
#
# A company wants to hire new employees. The budget of the company for the
# salaries is $70000. The company's criteria for hiring are:
#
# Hiring the largest number of seniors.
#
# After hiring the maximum number of seniors, use the remaining budget to
# hire the largest number of juniors.
#
# Write a solution to find the number of seniors and juniors hired under
# the mentioned criteria.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Candidates table:
# +-------------+------------+--------+
# | employee_id | experience | salary |
# +-------------+------------+--------+
# | 1           | Junior     | 10000  |
# | 9           | Junior     | 10000  |
# | 2           | Senior     | 20000  |
# | 11          | Senior     | 20000  |
# | 13          | Senior     | 50000  |
# | 4           | Junior     | 40000  |
# +-------------+------------+--------+
# Output:
# +------------+---------------------+
# | experience | accepted_candidates |
# +------------+---------------------+
# | Senior     | 2                   |
# | Junior     | 2                   |
# +------------+---------------------+
# Explanation:
# We can hire 2 seniors with IDs (2, 11). Since the budget is $70000 and
# the sum of their salaries is $40000, we still have $30000 but they are
# not enough to hire the senior candidate with ID 13.
# We can hire 2 juniors with IDs (1, 9). Since the remaining budget is
# $30000 and the sum of their salaries is $20000, we still have $10000 but
# they are not enough to hire the junior candidate with ID 4.
#
# Example 2:
#
# Input:
# Candidates table:
# +-------------+------------+--------+
# | employee_id | experience | salary |
# +-------------+------------+--------+
# | 1           | Junior     | 10000  |
# | 9           | Junior     | 10000  |
# | 2           | Senior     | 80000  |
# | 11          | Senior     | 80000  |
# | 13          | Senior     | 80000  |
# | 4           | Junior     | 40000  |
# +-------------+------------+--------+
# Output:
# +------------+---------------------+
# | experience | accepted_candidates |
# +------------+---------------------+
# | Senior     | 0                   |
# | Junior     | 3                   |
# +------------+---------------------+
# Explanation:
# We cannot hire any seniors with the current budget as we need at least
# $80000 to hire one senior.
# We can hire all three juniors with the remaining budget.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL: Candidates(employee_id, experience, salary). Budget 70000. Hire as
        many Seniors as possible (cheapest first), then Juniors with remainder.
        Return senior_cnt, junior_cnt.

        Algorithm:
        - Window SUM(salary) PARTITION BY experience ORDER BY salary.
        - Senior count where run<=70000; juniors where run <= leftover.

        Complexity: O(N log N).
        """
        self.sql = """
WITH cte AS (
  SELECT experience,
         SUM(salary) OVER (PARTITION BY experience ORDER BY salary ASC, employee_id ASC) AS run
  FROM Candidates
),
senior_spend AS (
  SELECT COALESCE(MAX(run), 0) AS spent
  FROM cte
  WHERE experience = 'Senior' AND run <= 70000
)
SELECT
  (SELECT COUNT(*) FROM cte WHERE experience = 'Senior' AND run <= 70000) AS senior_cnt,
  (SELECT COUNT(*) FROM cte, senior_spend
   WHERE experience = 'Junior' AND run <= 70000 - senior_spend.spent) AS junior_cnt;
"""
        return self.sql
# @lc code=end
