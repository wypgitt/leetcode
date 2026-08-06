#
# @lc app=leetcode id=2853 lang=python3
#
# [2853] Highest Salaries Difference
#
# https://leetcode.com/problems/highest-salaries-difference/description/
#
# database
# Easy (73.32%)
# Likes:    19
# Dislikes: 1
# Total Accepted:    6.4K
# Total Submissions: 8.7K
# Testcase Example:  "{\"headers\": {\"Salaries\": [\"emp_name\", \"department\", \"salary\"]},\"rows\":  {\"Salaries\": [[\"Kathy\",\"Engineering\",50000],[\"Roy\",\"Marketing\",30000],[\"Charles\",\"Engineering\",45000],[\"Jack\",\"Engineering\",85000],[\"Benjamin\",\"Marketing\",34000],[\"Anthony\",\"Marketing\",42000],[\"Edward\",\"Engineering\",102000],[\"Terry\",\"Engineering\",44000],[\"Evelyn\",\"Marketing\",53000],[\"Arthur\",\"Engineering\",32000]]}}"
#
#
# Table: Salaries
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | emp_name    | varchar |
# | department  | varchar |
# | salary      | int     |
# +-------------+---------+
# (emp_name, department) is the primary key (combination of unique values)
# for this table.
# Each row of this table contains emp_name, department and salary. There
# will be at least one entry for the engineering and marketing
# departments.
#
# Write a solution to calculate the difference between the highest
# salaries in the marketing and engineering department. Output the
# absolute difference in salaries.
#
# Return the result table.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Salaries table:
# +----------+-------------+--------+
# | emp_name | department  | salary |
# +----------+-------------+--------+
# | Kathy    | Engineering | 50000  |
# | Roy      | Marketing   | 30000  |
# | Charles  | Engineering | 45000  |
# | Jack     | Engineering | 85000  |
# | Benjamin | Marketing   | 34000  |
# | Anthony  | Marketing   | 42000  |
# | Edward   | Engineering | 102000 |
# | Terry    | Engineering | 44000  |
# | Evelyn   | Marketing   | 53000  |
# | Arthur   | Engineering | 32000  |
# +----------+-------------+--------+
# Output:
# +-------------------+
# | salary_difference |
# +-------------------+
# | 49000             |
# +-------------------+
# Explanation:
# - The Engineering and Marketing departments have the highest salaries of
# 102,000 and 53,000, respectively. Resulting in an absolute difference of
# 49,000.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Salaries(emp_name, department, salary). Absolute difference between
        the highest Engineering salary and the highest Marketing salary.

        Algorithm:
        - MAX(salary) filtered by each department (or GROUP BY then MAX-MIN of the two).

        Complexity: O(N).
        """
        self.sql = """
SELECT ABS(
  (SELECT MAX(salary) FROM Salaries WHERE department = 'Engineering')
  - (SELECT MAX(salary) FROM Salaries WHERE department = 'Marketing')
) AS salary_difference;
"""
        return self.sql
# @lc code=end
