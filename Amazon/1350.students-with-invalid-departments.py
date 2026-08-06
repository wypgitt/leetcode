#
# @lc app=leetcode id=1350 lang=python3
#
# [1350] Students With Invalid Departments
#
# https://leetcode.com/problems/students-with-invalid-departments/description/
#
# database
# Easy (89.69%)
# Likes:    184
# Dislikes: 9
# Total Accepted:    67.5K
# Total Submissions: 75.3K
# Testcase Example:  "{\"headers\":{\"Departments\":[\"id\",\"name\"],\"Students\":[\"id\",\"name\",\"department_id\"]},\"rows\":{\"Departments\":[[1,\"Electrical Engineering\"],[7,\"Computer Engineering\"],[13,\"Bussiness Administration\"]],\"Students\":[[23,\"Alice\",1],[1,\"Bob\",7],[5,\"Jennifer\",13],[2,\"John\",14],[4,\"Jasmine\",77],[3,\"Steve\",74],[6,\"Luis\",1],[8,\"Jonathan\",7],[7,\"Daiana\",33],[11,\"Madelynn\",1]]}}"
#
#
# Table: Departments
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | id            | int     |
# | name          | varchar |
# +---------------+---------+
# In SQL, id is the primary key of this table.
# The table has information about the id of each department of a
# university.
#
# Table: Students
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | id            | int     |
# | name          | varchar |
# | department_id | int     |
# +---------------+---------+
# In SQL, id is the primary key of this table.
# The table has information about the id of each student at a university
# and the id of the department he/she studies at.
#
# Find the id and the name of all students who are enrolled in departments
# that no longer exist.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Departments table:
# +------+--------------------------+
# | id   | name                     |
# +------+--------------------------+
# | 1    | Electrical Engineering   |
# | 7    | Computer Engineering     |
# | 13   | Bussiness Administration |
# +------+--------------------------+
# Students table:
# +------+----------+---------------+
# | id   | name     | department_id |
# +------+----------+---------------+
# | 23   | Alice    | 1             |
# | 1    | Bob      | 7             |
# | 5    | Jennifer | 13            |
# | 2    | John     | 14            |
# | 4    | Jasmine  | 77            |
# | 3    | Steve    | 74            |
# | 6    | Luis     | 1             |
# | 8    | Jonathan | 7             |
# | 7    | Daiana   | 33            |
# | 11   | Madelynn | 1             |
# +------+----------+---------------+
# Output:
# +------+----------+
# | id   | name     |
# +------+----------+
# | 2    | John     |
# | 7    | Daiana   |
# | 4    | Jasmine  |
# | 3    | Steve    |
# +------+----------+
# Explanation:
# John, Daiana, Steve, and Jasmine are enrolled in departments 14, 33, 74,
# and 77 respectively. department 14, 33, 74, and 77 do not exist in the
# Departments table.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Departments(id, name), Students(id, name, department_id).
        Return students whose department_id is not in Departments.

        Algorithm:
        - LEFT JOIN Departments; WHERE d.id IS NULL (or NOT IN / NOT EXISTS).

        Complexity: O(S+D).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT s.id, s.name
    FROM Students s
    LEFT JOIN Departments d ON s.department_id = d.id
    WHERE d.id IS NULL;
    """
# @lc code=end

