#
# @lc app=leetcode id=1965 lang=python3
#
# [1965] Employees With Missing Information
#
# https://leetcode.com/problems/employees-with-missing-information/description/
#
# algorithms
# Easy (73.41%)
# Likes:    807
# Dislikes: 41
# Total Accepted:    190K
# Total Submissions: 259K
# Testcase Example:  "{\"headers\":{\"Employees\":[\"employee_id\",\"name\"],\"Salaries\":[\"employee_id\",\"salary\"]},\"rows\":{\"Employees\":[[2,\"Crew\"],[4,\"Haven\"],[5,\"Kristian\"]],\"Salaries\":[[5,76071],[1,22517],[4,63539]]}}"
#
# Table: Employees
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | employee_id | int |
# | name | varchar |
# +-------------+---------+
# employee_id is the column with unique values for this table.
# Each row of this table indicates the name of the employee whose ID is
# employee_id.
#
# Table: Salaries
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | employee_id | int |
# | salary | int |
# +-------------+---------+
# employee_id is the column with unique values for this table.
# Each row of this table indicates the salary of the employee whose ID is
# employee_id.
#
# Write a solution to report the IDs of all the employees with missing
# information. The information of an employee is missing if:
#
# The employee's name is missing, or
#
# The employee's salary is missing.
#
# Return the result table ordered by employee_id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employees table:
# +-------------+----------+
# | employee_id | name |
# +-------------+----------+
# | 2 | Crew |
# | 4 | Haven |
# | 5 | Kristian |
# +-------------+----------+
# Salaries table:
# +-------------+--------+
# | employee_id | salary |
# +-------------+--------+
# | 5 | 76071 |
# | 1 | 22517 |
# | 4 | 63539 |
# +-------------+--------+
# Output:
# +-------------+
# | employee_id |
# +-------------+
# | 1 |
# | 2 |
# +-------------+
# Explanation:
# Employees 1, 2, 4, and 5 are working at this company.
# The name of employee 1 is missing.
# The salary of employee 2 is missing.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Employees with missing name or salary: IDs in Employees XOR Salaries.
        Return employee_id ordered ascending.

        Algorithm:
        - FULL OUTER / UNION of anti-joins on employee_id; ORDER BY employee_id.

        Complexity: O(N log N) with sort / hash anti-join O(N).
        """
        return self.sql

    sql = """
    SELECT employee_id
    FROM Employees
    WHERE employee_id NOT IN (SELECT employee_id FROM Salaries)
    UNION
    SELECT employee_id
    FROM Salaries
    WHERE employee_id NOT IN (SELECT employee_id FROM Employees)
    ORDER BY employee_id;
    """

    def solve_full_outer(self) -> str:
        """
        Interview explanation:
        Alternate: LEFT JOIN both ways (or FULL OUTER JOIN) and keep NULLs.

        Algorithm:
        - UNION of Employees LEFT JOIN Salaries WHERE salary IS NULL and the
          symmetric Salaries LEFT JOIN Employees WHERE name IS NULL.

        Complexity: O(N) hash joins + O(N log N) order.
        """
        return self.sql_full_outer

    sql_full_outer = """
    SELECT e.employee_id
    FROM Employees e
    LEFT JOIN Salaries s ON e.employee_id = s.employee_id
    WHERE s.salary IS NULL
    UNION
    SELECT s.employee_id
    FROM Salaries s
    LEFT JOIN Employees e ON e.employee_id = s.employee_id
    WHERE e.name IS NULL
    ORDER BY employee_id;
    """
# @lc code=end

