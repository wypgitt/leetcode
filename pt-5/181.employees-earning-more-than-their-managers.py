#
# @lc app=leetcode id=181 lang=python3
#
# [181] Employees Earning More Than Their Managers
#
# https://leetcode.com/problems/employees-earning-more-than-their-managers/description/
#
# algorithms
# Easy (73.67%)
# Likes:    3225
# Dislikes: 303
# Total Accepted:    1.3M
# Total Submissions: 1.7M
# Testcase Example:  "{\"headers\": {\"Employee\": [\"id\", \"name\", \"salary\", \"managerId\"]}, \"rows\": {\"Employee\": [[1, \"Joe\", 70000, 3], [2, \"Henry\", 80000, 4], [3, \"Sam\", 60000, null], [4, \"Max\", 90000, null]]}}"
#
# Table: Employee
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | id | int |
# | name | varchar |
# | salary | int |
# | managerId | int |
# +-------------+---------+
# id is the primary key (column with unique values) for this table.
# Each row of this table indicates the ID of an employee, their name, salary,
# and the ID of their manager.
#
# Write a solution to find the employees who earn more than their managers.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employee table:
# +----+-------+--------+-----------+
# | id | name | salary | managerId |
# +----+-------+--------+-----------+
# | 1 | Joe | 70000 | 3 |
# | 2 | Henry | 80000 | 4 |
# | 3 | Sam | 60000 | Null |
# | 4 | Max | 90000 | Null |
# +----+-------+--------+-----------+
# Output:
# +----------+
# | Employee |
# +----------+
# | Joe |
# +----------+
# Explanation: Joe is the only employee who earns more than his manager.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Self-join Employee as worker and manager; compare salaries after
        matching managerId to manager id.

        Algorithm:
        - JOIN Employee e to Employee m ON e.managerId = m.id.
        - WHERE e.salary > m.salary; SELECT e.name.

        Complexity: O(E) with index on id / managerId; otherwise join cost
        relative to Employee size.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT e.name AS Employee
    FROM Employee e
    JOIN Employee m
        ON e.managerId = m.id
    WHERE e.salary > m.salary;
    """
# @lc code=end
