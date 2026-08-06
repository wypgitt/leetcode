#
# @lc app=leetcode id=1789 lang=python3
#
# [1789] Primary Department for Each Employee
#
# https://leetcode.com/problems/primary-department-for-each-employee/description/
#
# algorithms
# Easy (75.04%)
# Likes:    902
# Dislikes: 274
# Total Accepted:    388K
# Total Submissions: 518K
# Testcase Example:  "{\"headers\":{\"Employee\":[\"employee_id\",\"department_id\",\"primary_flag\"]},\"rows\":{\"Employee\":[[\"1\",\"1\",\"N\"],[\"2\",\"1\",\"Y\"],[\"2\",\"2\",\"N\"],[\"3\",\"3\",\"N\"],[\"4\",\"2\",\"N\"],[\"4\",\"3\",\"Y\"],[\"4\",\"4\",\"N\"]]}}"
#
# Table: Employee
#
# +---------------+---------+
# | Column Name | Type |
# +---------------+---------+
# | employee_id | int |
# | department_id | int |
# | primary_flag | varchar |
# +---------------+---------+
# (employee_id, department_id) is the primary key (combination of columns with
# unique values) for this table.
# employee_id is the id of the employee.
# department_id is the id of the department to which the employee belongs.
# primary_flag is an ENUM (category) of type ('Y', 'N'). If the flag is 'Y',
# the department is the primary department for the employee. If the flag is
# 'N', the department is not the primary.
#
# Employees can belong to multiple departments. When the employee joins other
# departments, they need to decide which department is their primary
# department. Note that when an employee belongs to only one department, their
# primary column is 'N'.
#
# Write a solution to report all the employees with their primary department.
# For employees who belong to one department, report their only department.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employee table:
# +-------------+---------------+--------------+
# | employee_id | department_id | primary_flag |
# +-------------+---------------+--------------+
# | 1 | 1 | N |
# | 2 | 1 | Y |
# | 2 | 2 | N |
# | 3 | 3 | N |
# | 4 | 2 | N |
# | 4 | 3 | Y |
# | 4 | 4 | N |
# +-------------+---------------+--------------+
# Output:
# +-------------+---------------+
# | employee_id | department_id |
# +-------------+---------------+
# | 1 | 1 |
# | 2 | 1 |
# | 3 | 3 |
# | 4 | 3 |
# +-------------+---------------+
# Explanation:
# - The Primary department for employee 1 is 1.
# - The Primary department for employee 2 is 1.
# - The Primary department for employee 3 is 3.
# - The Primary department for employee 4 is 3.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Employee may have multiple departments; primary_flag='Y' marks the
        primary. If only one department, it is primary even if flag='N'.
        Return (employee_id, department_id) for each employee's primary dept.

        Algorithm:
        - SELECT where primary_flag='Y'
          UNION
          SELECT employees appearing once (GROUP BY HAVING COUNT=1).

        Complexity: O(N) with indexes / hash aggregation.
        """
        return self.sql

    sql = """
    SELECT employee_id, department_id
    FROM Employee
    WHERE primary_flag = 'Y'
    UNION
    SELECT employee_id, department_id
    FROM Employee
    GROUP BY employee_id
    HAVING COUNT(department_id) = 1;
    """

    def solve_window(self) -> str:
        """
        Interview explanation:
        Alternate SQL: window COUNT(*) OVER (PARTITION BY employee_id); keep
        rows that are flagged primary or are the employee's only department.

        Algorithm:
        - CTE with cnt = COUNT(*) OVER (PARTITION BY employee_id)
        - WHERE primary_flag='Y' OR cnt=1

        Complexity: O(N) with window aggregation.
        """
        return self.sql_window

    sql_window = """
    WITH t AS (
        SELECT employee_id, department_id, primary_flag,
               COUNT(*) OVER (PARTITION BY employee_id) AS cnt
        FROM Employee
    )
    SELECT employee_id, department_id
    FROM t
    WHERE primary_flag = 'Y' OR cnt = 1;
    """
# @lc code=end
