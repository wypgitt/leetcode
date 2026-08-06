#
# @lc app=leetcode id=1378 lang=python3
#
# [1378] Replace Employee ID With The Unique Identifier
#
# https://leetcode.com/problems/replace-employee-id-with-the-unique-identifier/description/
#
# algorithms
# Easy (83.72%)
# Likes:    2130
# Dislikes: 164
# Total Accepted:    1.4M
# Total Submissions: 1.7M
# Testcase Example:  "{\"headers\":{\"Employees\":[\"id\",\"name\"],\"EmployeeUNI\":[\"id\",\"unique_id\"]},\"rows\":{\"Employees\":[[1,\"Alice\"],[7,\"Bob\"],[11,\"Meir\"],[90,\"Winston\"],[3,\"Jonathan\"]],\"EmployeeUNI\":[[3,1],[11,2],[90,3]]}}"
#
# Table: Employees
#
# +---------------+---------+
# | Column Name | Type |
# +---------------+---------+
# | id | int |
# | name | varchar |
# +---------------+---------+
# id is the primary key (column with unique values) for this table.
# Each row of this table contains the id and the name of an employee in a
# company.
#
# Table: EmployeeUNI
#
# +---------------+---------+
# | Column Name | Type |
# +---------------+---------+
# | id | int |
# | unique_id | int |
# +---------------+---------+
# (id, unique_id) is the primary key (combination of columns with unique
# values) for this table.
# Each row of this table contains the id and the corresponding unique id of an
# employee in the company.
#
# Write a solution to show the unique ID of each user, If a user does not have
# a unique ID replace just show null.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employees table:
# +----+----------+
# | id | name |
# +----+----------+
# | 1 | Alice |
# | 7 | Bob |
# | 11 | Meir |
# | 90 | Winston |
# | 3 | Jonathan |
# +----+----------+
# EmployeeUNI table:
# +----+-----------+
# | id | unique_id |
# +----+-----------+
# | 3 | 1 |
# | 11 | 2 |
# | 90 | 3 |
# +----+-----------+
# Output:
# +-----------+----------+
# | unique_id | name |
# +-----------+----------+
# | null | Alice |
# | null | Bob |
# | 2 | Meir |
# | 3 | Winston |
# | 1 | Jonathan |
# +-----------+----------+
# Explanation:
# Alice and Bob do not have a unique ID, We will show null instead.
# The unique ID of Meir is 2.
# The unique ID of Winston is 3.
# The unique ID of Jonathan is 1.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Show each employee's unique_id (null if missing) with their name via
        LEFT JOIN from Employees to EmployeeUNI.

        Algorithm:
        - SELECT unique_id, name FROM Employees LEFT JOIN EmployeeUNI USING(id)

        Complexity: O(E + U) with hash join.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT eu.unique_id, e.name
    FROM Employees e
    LEFT JOIN EmployeeUNI eu ON e.id = eu.id;
    """
# @lc code=end
