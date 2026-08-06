#
# @lc app=leetcode id=184 lang=python3
#
# [184] Department Highest Salary
#
# https://leetcode.com/problems/department-highest-salary/description/
#
# algorithms
# Medium (58.94%)
# Likes:    2450
# Dislikes: 214
# Total Accepted:    729K
# Total Submissions: 1.2M
# Testcase Example:  "{\"headers\": {\"Employee\": [\"id\", \"name\", \"salary\", \"departmentId\"], \"Department\": [\"id\", \"name\"]}, \"rows\": {\"Employee\": [[1, \"Joe\", 70000, 1], [2, \"Jim\", 90000, 1], [3, \"Henry\", 80000, 2], [4, \"Sam\", 60000, 2], [5, \"Max\", 90000, 1]], \"Department\": [[1, \"IT\"], [2, \"Sales\"]]}}"
#
# Table: Employee
#
# +--------------+---------+
# | Column Name | Type |
# +--------------+---------+
# | id | int |
# | name | varchar |
# | salary | int |
# | departmentId | int |
# +--------------+---------+
# id is the primary key (column with unique values) for this table.
# departmentId is a foreign key (reference columns) of the ID from the
# Department table.
# Each row of this table indicates the ID, name, and salary of an employee. It
# also contains the ID of their department.
#
# Table: Department
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | id | int |
# | name | varchar |
# +-------------+---------+
# id is the primary key (column with unique values) for this table. It is
# guaranteed that department name is not NULL.
# Each row of this table indicates the ID of a department and its name.
#
# Write a solution to find employees who have the highest salary in each of the
# departments.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employee table:
# +----+-------+--------+--------------+
# | id | name | salary | departmentId |
# +----+-------+--------+--------------+
# | 1 | Joe | 70000 | 1 |
# | 2 | Jim | 90000 | 1 |
# | 3 | Henry | 80000 | 2 |
# | 4 | Sam | 60000 | 2 |
# | 5 | Max | 90000 | 1 |
# +----+-------+--------+--------------+
# Department table:
# +----+-------+
# | id | name |
# +----+-------+
# | 1 | IT |
# | 2 | Sales |
# +----+-------+
# Output:
# +------------+----------+--------+
# | Department | Employee | Salary |
# +------------+----------+--------+
# | IT | Jim | 90000 |
# | Sales | Henry | 80000 |
# | IT | Max | 90000 |
# +------------+----------+--------+
# Explanation: Max and Jim both have the highest salary in the IT department
# and Henry has the highest salary in the Sales department.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Per-department max salary via GROUP BY, then keep employees whose
        (departmentId, salary) pair matches that max (handles ties).

        Algorithm:
        - Subquery: departmentId, MAX(salary) GROUP BY departmentId.
        - Join Employee to Department; filter with IN on that pair.

        Complexity: O(E) to compute maxes + join to Department; indexes on
        departmentId / salary help.

        Alternate:
        - RANK/DENSE_RANK PARTITION BY departmentId ORDER BY salary DESC
          and filter rank = 1.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        d.name AS Department,
        e.name AS Employee,
        e.salary AS Salary
    FROM Employee e
    JOIN Department d
        ON e.departmentId = d.id
    WHERE (e.departmentId, e.salary) IN (
        SELECT departmentId, MAX(salary)
        FROM Employee
        GROUP BY departmentId
    );
    """
# @lc code=end
