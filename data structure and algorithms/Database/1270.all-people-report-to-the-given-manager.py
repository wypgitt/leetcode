#
# @lc app=leetcode id=1270 lang=python3
#
# [1270] All People Report to the Given Manager
#
# https://leetcode.com/problems/all-people-report-to-the-given-manager/description/
#
# database
# Medium (83.83%)
# Likes:    446
# Dislikes: 32
# Total Accepted:    68K
# Total Submissions: 81.1K
# Testcase Example:  "{\"headers\":{\"Employees\":[\"employee_id\",\"employee_name\",\"manager_id\"]},\"rows\":{\"Employees\":[[1,\"Boss\",1],[3,\"Alice\",3],[2,\"Bob\",1],[4,\"Daniel\",2],[7,\"Luis\",4],[8,\"John\",3],[9,\"Angela\",8],[77,\"Robert\",1]]}}"
#
#
# Table: Employees
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | employee_id   | int     |
# | employee_name | varchar |
# | manager_id    | int     |
# +---------------+---------+
# employee_id is the column of unique values for this table.
# Each row of this table indicates that the employee with ID employee_id
# and name employee_name reports his work to his/her direct manager with
# manager_id
# The head of the company is the employee with employee_id = 1.
#
# Write a solution to find employee_id of all employees that directly or
# indirectly report their work to the head of the company.
#
# The indirect relation between managers will not exceed three managers as
# the company is small.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employees table:
# +-------------+---------------+------------+
# | employee_id | employee_name | manager_id |
# +-------------+---------------+------------+
# | 1           | Boss          | 1          |
# | 3           | Alice         | 3          |
# | 2           | Bob           | 1          |
# | 4           | Daniel        | 2          |
# | 7           | Luis          | 4          |
# | 8           | Jhon          | 3          |
# | 9           | Angela        | 8          |
# | 77          | Robert        | 1          |
# +-------------+---------------+------------+
# Output:
# +-------------+
# | employee_id |
# +-------------+
# | 2           |
# | 77          |
# | 4           |
# | 7           |
# +-------------+
# Explanation:
# The head of the company is the employee with employee_id 1.
# The employees with employee_id 2 and 77 report their work directly to
# the head of the company.
# The employee with employee_id 4 reports their work indirectly to the
# head of the company 4 --> 2 --> 1.
# The employee with employee_id 7 reports their work indirectly to the
# head of the company 7 --> 4 --> 2 --> 1.
# The employees with employee_id 3, 8, and 9 do not report their work to
# the head of the company directly or indirectly.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Find employees who report (directly or indirectly) to manager
        1 with at most 3 levels of managers between them — i.e. employee_id
        whose manager chain within 3 hops reaches 1. Classic self-join on
        Employees three times.

        Algorithm:
        - Self-join e1->e2->e3 on manager_id; select distinct employee_id
          where any of e1/e2/e3.manager_id = 1 and employee_id != 1.

        Complexity: O(N) with joins on indexed manager_id.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT DISTINCT e1.employee_id
    FROM Employees e1
    LEFT JOIN Employees e2 ON e1.manager_id = e2.employee_id
    LEFT JOIN Employees e3 ON e2.manager_id = e3.employee_id
    WHERE 1 IN (e1.manager_id, e2.manager_id, e3.manager_id)
      AND e1.employee_id != 1;
    """
# @lc code=end
