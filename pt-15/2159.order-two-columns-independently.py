#
# @lc app=leetcode id=2159 lang=python3
#
# [2159] Order Two Columns Independently
#
# https://leetcode.com/problems/order-two-columns-independently/description/
#
# database
# Medium (61.82%)
# Likes:    80
# Dislikes: 19
# Total Accepted:    11.2K
# Total Submissions: 18.1K
# Testcase Example:  "{\"headers\":{\"Data\":[\"first_col\",\"second_col\"]},\"rows\":{\"Data\":[[4,2],[2,3],[3,1],[1,4]]}}"
#
#
# Table: Data
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | first_col   | int  |
# | second_col  | int  |
# +-------------+------+
# This table may contain duplicate rows.
#
# Write a solution to independently:
#
# order first_col in ascending order.
#
# order second_col in descending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Data table:
# +-----------+------------+
# | first_col | second_col |
# +-----------+------------+
# | 4         | 2          |
# | 2         | 3          |
# | 3         | 1          |
# | 1         | 4          |
# +-----------+------------+
# Output:
# +-----------+------------+
# | first_col | second_col |
# +-----------+------------+
# | 1         | 4          |
# | 2         | 3          |
# | 3         | 2          |
# | 4         | 1          |
# +-----------+------------+
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Data(first_col, second_col). Independently sort first_col
        ascending and second_col descending, then zip by row number.

        Algorithm:
        - ROW_NUMBER() OVER (ORDER BY first_col) and OVER (ORDER BY second_col
          DESC); JOIN on row number.

        Complexity: O(N log N) sort.
        """
        return self.sql

    sql = """
    WITH
    S AS (
        SELECT first_col, ROW_NUMBER() OVER (ORDER BY first_col) AS rk
        FROM Data
    ),
    T AS (
        SELECT second_col, ROW_NUMBER() OVER (ORDER BY second_col DESC) AS rk
        FROM Data
    )
    SELECT S.first_col, T.second_col
    FROM S
    JOIN T USING (rk);
    """
# @lc code=end
