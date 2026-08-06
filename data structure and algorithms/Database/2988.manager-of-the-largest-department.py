#
# @lc app=leetcode id=2988 lang=python3
#
# [2988] Manager of the Largest Department
#
# https://leetcode.com/problems/manager-of-the-largest-department/description/
#
# database
# Medium (80.75%)
# Likes:    9
# Dislikes: 1
# Total Accepted:    4.9K
# Total Submissions: 6K
# Testcase Example:  "{\"headers\":{\"Employees\":[\"emp_id\",\"emp_name\",\"dep_id\",\"position\"]},\"rows\":{\"Employees\":[[156,\"Michael\",107,\"Manager\"],[112,\"Lucas\",107,\"Consultant\"],[8,\"Isabella\",101,\"Manager\"],[160,\"Joseph\",100,\"Manager\"],[80,\"Aiden\",100,\"Engineer\"],[190,\"Skylar\",100,\"Freelancer\"],[196,\"Stella\",101,\"Coordinator\"],[167,\"Audrey\",100,\"Consultant\"],[97,\"Nathan\",101,\"Supervisor\"],[128,\"Ian\",101,\"Administrator\"],[81,\"Ethan\",107,\"Administrator\"]]}}"
#
#
# Table: Employees
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | emp_id      | int     |
# | emp_name    | varchar |
# | dep_id      | int     |
# | position    | varchar |
# +-------------+---------+
# emp_id is column of unique values for this table.
# This table contains emp_id, emp_name, dep_id, and position.
#
# Write a solution to find the name of the manager from the largest
# department. There may be multiple largest departments when the number of
# employees in those departments is the same.
#
# Return the result table sorted by dep_id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employees table:
# +--------+----------+--------+---------------+
# | emp_id | emp_name | dep_id | position      |
# +--------+----------+--------+---------------+
# | 156    | Michael  | 107    | Manager       |
# | 112    | Lucas    | 107    | Consultant    |
# | 8      | Isabella | 101    | Manager       |
# | 160    | Joseph   | 100    | Manager       |
# | 80     | Aiden    | 100    | Engineer      |
# | 190    | Skylar   | 100    | Freelancer    |
# | 196    | Stella   | 101    | Coordinator   |
# | 167    | Audrey   | 100    | Consultant    |
# | 97     | Nathan   | 101    | Supervisor    |
# | 128    | Ian      | 101    | Administrator |
# | 81     | Ethan    | 107    | Administrator |
# +--------+----------+--------+---------------+
# Output
# +--------------+--------+
# | manager_name | dep_id |
# +--------------+--------+
# | Joseph       | 100    |
# | Isabella     | 101    |
# +--------------+--------+
# Explanation
# - Departments with IDs 100 and 101 each has a total of 4 employees,
# while department 107 has 3 employees. Since both departments 100 and 101
# have an equal number of employees, their respective managers will be
# included.
# Output table is ordered by dep_id in ascending order.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Employees(emp_id, emp_name, dep_id, position). Return
        manager_name and dep_id for every largest department (by headcount;
        ties keep all). Order by dep_id ASC.

        Algorithm:
        - CTE of dep sizes; join Managers; filter cnt = MAX(cnt).

        Complexity: O(N).
        """
        self.sql = """
WITH
    T AS (
        SELECT dep_id, COUNT(1) AS cnt
        FROM Employees
        GROUP BY 1
    )
SELECT emp_name AS manager_name, t.dep_id
FROM
    T AS t
    JOIN Employees AS e ON t.dep_id = e.dep_id AND e.position = 'Manager'
WHERE cnt = (SELECT MAX(cnt) FROM T)
ORDER BY 2;
"""
        return self.sql
# @lc code=end
