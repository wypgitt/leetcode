#
# @lc app=leetcode id=570 lang=python3
#
# [570] Managers with at Least 5 Direct Reports
#
# https://leetcode.com/problems/managers-with-at-least-5-direct-reports/description/
#
# algorithms
# Medium (49.33%)
# Likes:    1841
# Dislikes: 194
# Total Accepted:    1.0M
# Total Submissions: 2.1M
# Testcase Example:  "{\"headers\": {\"Employee\": [\"id\", \"name\", \"department\", \"managerId\"]}, \"rows\": {\"Employee\": [[101, \"John\", \"A\", null],[102, \"Dan\", \"A\", 101], [103, \"James\", \"A\", 101], [104, \"Amy\", \"A\", 101], [105, \"Anne\", \"A\", 101], [106, \"Ron\", \"B\", 101]]}}"
#
# Table: Employee
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | id | int |
# | name | varchar |
# | department | varchar |
# | managerId | int |
# +-------------+---------+
# id is the primary key (column with unique values) for this table.
# Each row of this table indicates the name of an employee, their department,
# and the id of their manager.
# If managerId is null, then the employee does not have a manager.
# No employee will be the manager of themself.
#
# Write a solution to find managers with at least five direct reports.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employee table:
# +-----+-------+------------+-----------+
# | id | name | department | managerId |
# +-----+-------+------------+-----------+
# | 101 | John | A | null |
# | 102 | Dan | A | 101 |
# | 103 | James | A | 101 |
# | 104 | Amy | A | 101 |
# | 105 | Anne | A | 101 |
# | 106 | Ron | B | 101 |
# +-----+-------+------------+-----------+
# Output:
# +------+
# | name |
# +------+
# | John |
# +------+
#


# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Count direct reports per managerId, keep managers with count >= 5,
        then join back to Employee for the name.

        Algorithm:
        - GROUP BY managerId HAVING COUNT(*) >= 5 (or join a subquery).
        - SELECT name of those manager ids.

        Complexity: O(E) scan/group over Employee.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT e.name
    FROM Employee e
    JOIN (
        SELECT managerId
        FROM Employee
        WHERE managerId IS NOT NULL
        GROUP BY managerId
        HAVING COUNT(*) >= 5
    ) m
        ON e.id = m.managerId;
    """
# @lc code=end

