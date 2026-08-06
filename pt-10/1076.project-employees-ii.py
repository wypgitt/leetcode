#
# @lc app=leetcode id=1076 lang=python3
#
# [1076] Project Employees II
#
# https://leetcode.com/problems/project-employees-ii/description/
#
# database
# Easy (50.47%)
# Likes:    207
# Dislikes: 63
# Total Accepted:    67.5K
# Total Submissions: 133.8K
# Testcase Example:  "{\"headers\":{\"Project\":[\"project_id\",\"employee_id\"],\"Employee\":[\"employee_id\",\"name\",\"experience_years\"]},\"rows\":{\"Project\":[[1,1],[1,2],[1,3],[2,1],[2,4]],\"Employee\":[[1,\"Khaled\",3],[2,\"Ali\",2],[3,\"John\",1],[4,\"Doe\",2]]}}"
#
#
# Table: Project
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | project_id  | int     |
# | employee_id | int     |
# +-------------+---------+
# (project_id, employee_id) is the primary key (combination of columns
# with unique values) of this table.
# employee_id is a foreign key (reference column) to Employee table.
# Each row of this table indicates that the employee with employee_id is
# working on the project with project_id.
#
# Table: Employee
#
# +------------------+---------+
# | Column Name      | Type    |
# +------------------+---------+
# | employee_id      | int     |
# | name             | varchar |
# | experience_years | int     |
# +------------------+---------+
# employee_id is the primary key (column with unique values) of this
# table.
# Each row of this table contains information about one employee.
#
# Write a solution to report all the projects that have the most
# employees.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Project table:
# +-------------+-------------+
# | project_id  | employee_id |
# +-------------+-------------+
# | 1           | 1           |
# | 1           | 2           |
# | 1           | 3           |
# | 2           | 1           |
# | 2           | 4           |
# +-------------+-------------+
# Employee table:
# +-------------+--------+------------------+
# | employee_id | name   | experience_years |
# +-------------+--------+------------------+
# | 1           | Khaled | 3                |
# | 2           | Ali    | 2                |
# | 3           | John   | 1                |
# | 4           | Doe    | 2                |
# +-------------+--------+------------------+
# Output:
# +-------------+
# | project_id  |
# +-------------+
# | 1           |
# +-------------+
# Explanation: The first project has 3 employees while the second one has
# 2.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Report project_id(s) that have the most employees (largest
        team size). Ties return all such projects.

        Algorithm:
        - Count employees per project_id.
        - Keep rows where cnt equals the global MAX(cnt).

        Complexity: O(P) aggregation.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT project_id
    FROM Project
    GROUP BY project_id
    HAVING COUNT(employee_id) = (
        SELECT COUNT(employee_id)
        FROM Project
        GROUP BY project_id
        ORDER BY COUNT(employee_id) DESC
        LIMIT 1
    );
    """
# @lc code=end
