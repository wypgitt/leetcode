#
# @lc app=leetcode id=1445 lang=python3
#
# [1445] Apples & Oranges
#
# https://leetcode.com/problems/apples-oranges/description/
#
# database
# Medium (86.00%)
# Likes:    251
# Dislikes: 23
# Total Accepted:    66.9K
# Total Submissions: 77.8K
# Testcase Example:  "{\"headers\":{\"Sales\":[\"sale_date\",\"fruit\",\"sold_num\"]},\"rows\":{\"Sales\":[[\"2020-05-01\",\"apples\",10],[\"2020-05-01\",\"oranges\",8],[\"2020-05-02\",\"apples\",15],[\"2020-05-02\",\"oranges\",15],[\"2020-05-03\",\"apples\",20],[\"2020-05-03\",\"oranges\",0],[\"2020-05-04\",\"apples\",15],[\"2020-05-04\",\"oranges\",16]]}}"
#
#
# Table: Sales
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | sale_date     | date    |
# | fruit         | enum    |
# | sold_num      | int     |
# +---------------+---------+
# (sale_date, fruit) is the primary key (combination of columns with
# unique values) of this table.
# This table contains the sales of "apples" and "oranges" sold each day.
#
# Write a solution to report the difference between the number of apples
# and oranges sold each day.
#
# Return the result table ordered by sale_date.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Sales table:
# +------------+------------+-------------+
# | sale_date  | fruit      | sold_num    |
# +------------+------------+-------------+
# | 2020-05-01 | apples     | 10          |
# | 2020-05-01 | oranges    | 8           |
# | 2020-05-02 | apples     | 15          |
# | 2020-05-02 | oranges    | 15          |
# | 2020-05-03 | apples     | 20          |
# | 2020-05-03 | oranges    | 0           |
# | 2020-05-04 | apples     | 15          |
# | 2020-05-04 | oranges    | 16          |
# +------------+------------+-------------+
# Output:
# +------------+--------------+
# | sale_date  | diff         |
# +------------+--------------+
# | 2020-05-01 | 2            |
# | 2020-05-02 | 0            |
# | 2020-05-03 | 20           |
# | 2020-05-04 | -1           |
# +------------+--------------+
# Explanation:
# Day 2020-05-01, 10 apples and 8 oranges were sold (Difference  10 - 8 =
# 2).
# Day 2020-05-02, 15 apples and 15 oranges were sold (Difference 15 - 15 =
# 0).
# Day 2020-05-03, 20 apples and 0 oranges were sold (Difference 20 - 0 =
# 20).
# Day 2020-05-04, 15 apples and 16 oranges were sold (Difference 15 - 16 =
# -1).
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Sales(sale_date, fruit, sold_num) with apples & oranges
        each day. Report sale_date and diff = apples - oranges ordered by date.

        Algorithm:
        - Self-join or conditional aggregation GROUP BY sale_date.

        Complexity: O(N).
        """
        return self.sql

    sql = """
    SELECT sale_date,
           SUM(CASE WHEN fruit = 'apples' THEN sold_num ELSE -sold_num END) AS diff
    FROM Sales
    GROUP BY sale_date
    ORDER BY sale_date;
    """
# @lc code=end
