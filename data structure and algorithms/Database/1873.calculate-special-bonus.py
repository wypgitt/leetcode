#
# @lc app=leetcode id=1873 lang=python3
#
# [1873] Calculate Special Bonus
#
# https://leetcode.com/problems/calculate-special-bonus/description/
#
# algorithms
# Easy (57.11%)
# Likes:    1200
# Dislikes: 83
# Total Accepted:    362K
# Total Submissions: 633K
# Testcase Example:  "{\"headers\":{\"Employees\":[\"employee_id\",\"name\",\"salary\"]},\"rows\":{\"Employees\":[[2,\"Meir\",3000],[3,\"Michael\",3800],[7,\"Addilyn\",7400],[8,\"Juan\",6100],[9,\"Kannon\",7700]]}}"
#
# Table: Employees
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | employee_id | int |
# | name | varchar |
# | salary | int |
# +-------------+---------+
# employee_id is the primary key (column with unique values) for this table.
# Each row of this table indicates the employee ID, employee name, and salary.
#
# Write a solution to calculate the bonus of each employee. The bonus of an
# employee is 100% of their salary if the ID of the employee is an odd number
# and the employee's name does not start with the character 'M'. The bonus of
# an employee is 0 otherwise.
#
# Return the result table ordered by employee_id.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employees table:
# +-------------+---------+--------+
# | employee_id | name | salary |
# +-------------+---------+--------+
# | 2 | Meir | 3000 |
# | 3 | Michael | 3800 |
# | 7 | Addilyn | 7400 |
# | 8 | Juan | 6100 |
# | 9 | Kannon | 7700 |
# +-------------+---------+--------+
# Output:
# +-------------+-------+
# | employee_id | bonus |
# +-------------+-------+
# | 2 | 0 |
# | 3 | 0 |
# | 7 | 7400 |
# | 8 | 0 |
# | 9 | 7700 |
# +-------------+-------+
# Explanation:
# The employees with IDs 2 and 8 get 0 bonus because they have an even
# employee_id.
# The employee with ID 3 gets 0 bonus because their name starts with 'M'.
# The rest of the employees get a 100% bonus.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Employees(employee_id, name, salary). Bonus = salary if employee_id odd
        AND name does not start with 'M'; else 0. Order by employee_id.

        Algorithm:
        - SELECT employee_id, CASE WHEN ... THEN salary ELSE 0 END AS bonus
          FROM Employees ORDER BY employee_id.

        Complexity: O(N).
        """
        return self.sql

    sql = """
    SELECT employee_id,
           CASE
               WHEN employee_id % 2 = 1 AND name NOT LIKE 'M%' THEN salary
               ELSE 0
           END AS bonus
    FROM Employees
    ORDER BY employee_id;
    """

    def solve_if(self) -> str:
        """
        Interview explanation:
        Alternate MySQL: IF(condition, salary, 0).

        Algorithm:
        - SELECT employee_id, IF(employee_id%2=1 AND name NOT LIKE 'M%', salary, 0)

        Complexity: O(N).
        """
        return self.sql_if

    sql_if = """
    SELECT employee_id,
           IF(employee_id % 2 = 1 AND name NOT LIKE 'M%', salary, 0) AS bonus
    FROM Employees
    ORDER BY employee_id;
    """
# @lc code=end
