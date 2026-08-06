#
# @lc app=leetcode id=1303 lang=python3
#
# [1303] Find the Team Size
#
# https://leetcode.com/problems/find-the-team-size/description/
#
# database
# Easy (89.54%)
# Likes:    344
# Dislikes: 16
# Total Accepted:    82.6K
# Total Submissions: 92.2K
# Testcase Example:  "{\"headers\":{\"Employee\":[\"employee_id\",\"team_id\"]},\"rows\":{\"Employee\":[[1,8],[2,8],[3,8],[4,7],[5,9],[6,9]]}}"
#
#
# Table: Employee
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | employee_id   | int     |
# | team_id       | int     |
# +---------------+---------+
# employee_id is the primary key (column with unique values) for this
# table.
# Each row of this table contains the ID of each employee and their
# respective team.
#
# Write a solution to find the team size of each of the employees.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employee Table:
# +-------------+------------+
# | employee_id | team_id    |
# +-------------+------------+
# |     1       |     8      |
# |     2       |     8      |
# |     3       |     8      |
# |     4       |     7      |
# |     5       |     9      |
# |     6       |     9      |
# +-------------+------------+
# Output:
# +-------------+------------+
# | employee_id | team_size  |
# +-------------+------------+
# |     1       |     3      |
# |     2       |     3      |
# |     3       |     3      |
# |     4       |     1      |
# |     5       |     2      |
# |     6       |     2      |
# +-------------+------------+
# Explanation:
# Employees with Id 1,2,3 are part of a team with team_id = 8.
# Employee with Id 4 is part of a team with team_id = 7.
# Employees with Id 5,6 are part of a team with team_id = 9.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Employee(employee_id, team_id). Return each employee with
        their team size (count of employees on the same team).

        Algorithm:
        - COUNT(*) OVER (PARTITION BY team_id) AS team_size.

        Complexity: O(N) aggregation.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        employee_id,
        COUNT(*) OVER (PARTITION BY team_id) AS team_size
    FROM Employee;
    """
# @lc code=end

