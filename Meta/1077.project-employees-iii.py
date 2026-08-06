#
# @lc app=leetcode id=1077 lang=python3
#
# [1077] Project Employees III
#
# https://leetcode.com/problems/project-employees-iii/description/
#
# database
# Medium (77.20%)
# Likes:    283
# Dislikes: 9
# Total Accepted:    73.6K
# Total Submissions: 95.3K
# Testcase Example:  "{\"headers\":{\"Project\":[\"project_id\",\"employee_id\"],\"Employee\":[\"employee_id\",\"name\",\"experience_years\"]},\"rows\":{\"Project\":[[1,1],[1,2],[1,3],[2,1],[2,4]],\"Employee\":[[1,\"Khaled\",3],[2,\"Ali\",2],[3,\"John\",3],[4,\"Doe\",2]]}}"
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
# Write a solution to report the most experienced employees in each
# project. In case of a tie, report all employees with the maximum number
# of experience years.
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
# | 3           | John   | 3                |
# | 4           | Doe    | 2                |
# +-------------+--------+------------------+
# Output:
# +-------------+---------------+
# | project_id  | employee_id   |
# +-------------+---------------+
# | 1           | 1             |
# | 1           | 3             |
# | 2           | 1             |
# +-------------+---------------+
# Explanation: Both employees with id 1 and 3 have the most experience
# among the employees of the first project. For the second project, the
# employee with id 1 has the most experience.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. For each project, return the employee(s) with the highest
        experience_years on that project (ties included).

        Algorithm:
        - JOIN Project⋈Employee.
        - Keep rows where experience_years equals MAX experience for that project
          (correlated subquery or window RANK).

        Complexity: O(P log P) with window / O(P·E) naive.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT p.project_id, p.employee_id
    FROM Project p
    JOIN Employee e ON p.employee_id = e.employee_id
    WHERE e.experience_years = (
        SELECT MAX(e2.experience_years)
        FROM Project p2
        JOIN Employee e2 ON p2.employee_id = e2.employee_id
        WHERE p2.project_id = p.project_id
    );
    """
# @lc code=end
