#
# @lc app=leetcode id=177 lang=python3
#
# [177] Nth Highest Salary
#
# https://leetcode.com/problems/nth-highest-salary/description/
#
# algorithms
# Medium (39.81%)
# Likes:    2346
# Dislikes: 1126
# Total Accepted:    723K
# Total Submissions: 1.8M
# Testcase Example:  "{\"headers\": {\"Employee\": [\"id\", \"salary\"]}, \"argument\": 2, \"rows\": {\"Employee\": [[1, 100], [2, 200], [3, 300]]}}"
#
# Table: Employee
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | id | int |
# | salary | int |
# +-------------+------+
# id is the primary key (column with unique values) for this table.
# Each row of this table contains information about the salary of an employee.
#
# Write a solution to find the n^th highest distinct salary from the Employee
# table. If there are less than n distinct salaries, return null.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Employee table:
# +----+--------+
# | id | salary |
# +----+--------+
# | 1 | 100 |
# | 2 | 200 |
# | 3 | 300 |
# +----+--------+
# n = 2
# Output:
# +------------------------+
# | getNthHighestSalary(2) |
# +------------------------+
# | 200 |
# +------------------------+
#
# Example 2:
#
# Input:
# Employee table:
# +----+--------+
# | id | salary |
# +----+--------+
# | 1 | 100 |
# +----+--------+
# n = 2
# Output:
# +------------------------+
# | getNthHighestSalary(2) |
# +------------------------+
# | null |
# +------------------------+
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Nth highest distinct salary via ORDER BY DESC + LIMIT/OFFSET. Adjust
        N to N-1 because OFFSET is 0-based; empty result yields NULL.

        Algorithm:
        - CREATE FUNCTION getNthHighestSalary(N).
        - SET N = N - 1; SELECT DISTINCT salary ORDER BY salary DESC
          LIMIT 1 OFFSET N.

        Complexity: sort/distinct over distinct salaries; indexes on salary
        help the ordered scan.

        Alternate:
        - DENSE_RANK() OVER (ORDER BY salary DESC) and filter rnk = N.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor (MySQL function form)
    sql = """
    CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT
    BEGIN
      SET N = N - 1;
      RETURN (
        SELECT DISTINCT salary
        FROM Employee
        ORDER BY salary DESC
        LIMIT 1 OFFSET N
      );
    END
    """
# @lc code=end
