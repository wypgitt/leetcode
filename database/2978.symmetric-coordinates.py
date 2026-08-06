#
# @lc app=leetcode id=2978 lang=python3
#
# [2978] Symmetric Coordinates
#
# https://leetcode.com/problems/symmetric-coordinates/description/
#
# database
# Medium (41.00%)
# Likes:    15
# Dislikes: 3
# Total Accepted:    3.3K
# Total Submissions: 8.1K
# Testcase Example:  "{\"headers\":{\"Coordinates\":[\"X\",\"Y\"]},\"rows\":{\"Coordinates\":[[20,20],[20,20],[20,21],[23,22],[22,23],[21,20]]}}"
#
#
# Table: Coordinates
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | X           | int  |
# | Y           | int  |
# +-------------+------+
# Each row includes X and Y, where both are integers. Table may contain
# duplicate values.
#
# Two coordindates (X1, Y1) and (X2, Y2) are said to be symmetric
# coordintes if X1 == Y2 and X2 == Y1.
#
# Write a solution that outputs, among all these symmetric coordintes,
# only those unique coordinates that satisfy the condition X1 <= Y1.
#
# Return the result table ordered by X and  Y (respectively) in ascending
# order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Coordinates table:
# +----+----+
# | X  | Y  |
# +----+----+
# | 20 | 20 |
# | 20 | 20 |
# | 20 | 21 |
# | 23 | 22 |
# | 22 | 23 |
# | 21 | 20 |
# +----+----+
# Output:
# +----+----+
# | x  | y  |
# +----+----+
# | 20 | 20 |
# | 20 | 21 |
# | 22 | 23 |
# +----+----+
# Explanation:
# - (20, 20) and (20, 20) are symmetric coordinates because, X1 == Y2 and
# X2 == Y1. This results in displaying (20, 20) as a distinctive
# coordinates.
# - (20, 21) and (21, 20) are symmetric coordinates because, X1 == Y2 and
# X2 == Y1. However, only (20, 21) will be displayed because X1 <= Y1.
# - (23, 22) and (22, 23) are symmetric coordinates because, X1 == Y2 and
# X2 == Y1. However, only (22, 23) will be displayed because X1 <= Y1.
# The output table is sorted by X and Y in ascending order.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Coordinates(X, Y) may have duplicates. Symmetric pairs satisfy
        (X1,Y1) ↔ (X2,Y2) with X1=Y2 and X2=Y1. Output unique rows with X <= Y,
        ordered by X, Y.

        Algorithm:
        - ROW_NUMBER to distinguish duplicate rows; self-join on the symmetry condition
          with id inequality; DISTINCT and ORDER BY.

        Complexity: O(N^2) join worst case.
        """
        self.sql = """
WITH
  P AS (
    SELECT
      ROW_NUMBER() OVER () AS id,
      X,
      Y
    FROM Coordinates
  )
SELECT DISTINCT
  p1.X,
  p1.Y
FROM P AS p1
JOIN P AS p2
  ON p1.X = p2.Y
 AND p1.Y = p2.X
 AND p1.X <= p1.Y
 AND p1.id != p2.id
ORDER BY 1, 2;
"""
        return self.sql
# @lc code=end
