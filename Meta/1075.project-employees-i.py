#
# @lc app=leetcode id=1075 lang=python3
#
# [1075] Project Employees I
#
# https://leetcode.com/problems/project-employees-i/description/
#
# algorithms
# Easy (67.13%)
# Likes:    1081
# Dislikes: 208
# Total Accepted:    741K
# Total Submissions: 1.1M
# Testcase Example:  "{\"headers\":{\"Project\":[\"project_id\",\"employee_id\"],\"Employee\":[\"employee_id\",\"name\",\"experience_years\"]},\"rows\":{\"Project\":[[1,1],[1,2],[1,3],[2,1],[2,4]],\"Employee\":[[1,\"Khaled\",3],[2,\"Ali\",2],[3,\"John\",1],[4,\"Doe\",2]]}}"
#
# Table: Project
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | project_id | int |
# | employee_id | int |
# +-------------+---------+
# (project_id, employee_id) is the primary key of this table.
# employee_id is a foreign key to Employee table.
# Each row of this table indicates that the employee with employee_id is
# working on the project with project_id.
#
# Table: Employee
#
# +------------------+---------+
# | Column Name | Type |
# +------------------+---------+
# | employee_id | int |
# | name | varchar |
# | experience_years | int |
# +------------------+---------+
# employee_id is the primary key of this table. It's guaranteed that
# experience_years is not NULL.
# Each row of this table contains information about one employee.
#
# Write an SQL query that reports the average experience years of all the
# employees for each project, rounded to 2 digits.
#
# Return the result table in any order.
#
# The query result format is in the following example.
#
# Example 1:
#
# Input:
# Project table:
# +-------------+-------------+
# | project_id | employee_id |
# +-------------+-------------+
# | 1 | 1 |
# | 1 | 2 |
# | 1 | 3 |
# | 2 | 1 |
# | 2 | 4 |
# +-------------+-------------+
# Employee table:
# +-------------+--------+------------------+
# | employee_id | name | experience_years |
# +-------------+--------+------------------+
# | 1 | Khaled | 3 |
# | 2 | Ali | 2 |
# | 3 | John | 1 |
# | 4 | Doe | 2 |
# +-------------+--------+------------------+
# Output:
# +-------------+---------------+
# | project_id | average_years |
# +-------------+---------------+
# | 1 | 2.00 |
# | 2 | 2.50 |
# +-------------+---------------+
# Explanation: The average experience years for the first project is (3 + 2 +
# 1) / 3 = 2.00 and for the second project is (3 + 2) / 2 = 2.50
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Average experience_years of employees on each project, rounded to 2 decimals.

        Algorithm:
        - JOIN Project with Employee on employee_id.
        - GROUP BY project_id; ROUND(AVG(experience_years), 2).

        Complexity: O(P + E) with hash join / aggregation.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT p.project_id,
           ROUND(AVG(e.experience_years), 2) AS average_years
    FROM Project p
    JOIN Employee e ON p.employee_id = e.employee_id
    GROUP BY p.project_id;
    """
# @lc code=end
