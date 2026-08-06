#
# @lc app=leetcode id=1853 lang=python3
#
# [1853] Convert Date Format
#
# https://leetcode.com/problems/convert-date-format/description/
#
# database
# Easy (84.72%)
# Likes:    69
# Dislikes: 42
# Total Accepted:    16.3K
# Total Submissions: 19.3K
# Testcase Example:  "{\"headers\":{\"Days\":[\"day\"]},\"rows\":{\"Days\":[[\"2022-04-12\"],[\"2021-08-09\"],[\"2020-06-26\"]]}}"
#
#
# Table: Days
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | day         | date |
# +-------------+------+
# day is the column with unique values for this table.
#
# Write a solution to convert each date in Days into a string formatted as
# "day_name, month_name day, year".
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Days table:
# +------------+
# | day        |
# +------------+
# | 2022-04-12 |
# | 2021-08-09 |
# | 2020-06-26 |
# +------------+
# Output:
# +-------------------------+
# | day                     |
# +-------------------------+
# | Tuesday, April 12, 2022 |
# | Monday, August 9, 2021  |
# | Friday, June 26, 2020   |
# +-------------------------+
# Explanation: Please note that the output is case-sensitive.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Days(day DATE). Convert each day to format
        'Day Month, Year' e.g. 'Tuesday April, 2022'.

        Algorithm:
        - SELECT DATE_FORMAT(day, '%W %M, %Y') AS day FROM Days;

        Complexity: O(N) rows scanned.
        """
        return self.sql

    sql = """
    SELECT DATE_FORMAT(day, '%W %M, %Y') AS day
    FROM Days;
    """

    def solve_concat(self) -> str:
        """
        Interview explanation:
        Alternate SQL: concatenate DAYNAME / MONTHNAME / YEAR explicitly.

        Algorithm:
        - SELECT CONCAT(DAYNAME(day), ' ', MONTHNAME(day), ', ', YEAR(day)) AS day

        Complexity: O(N).
        """
        return self.sql_concat

    sql_concat = """
    SELECT CONCAT(DAYNAME(day), ' ', MONTHNAME(day), ', ', YEAR(day)) AS day
    FROM Days;
    """
# @lc code=end
