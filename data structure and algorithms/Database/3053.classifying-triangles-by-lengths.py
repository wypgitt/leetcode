#
# @lc app=leetcode id=3053 lang=python3
#
# [3053] Classifying Triangles by Lengths
#
# https://leetcode.com/problems/classifying-triangles-by-lengths/description/
#
# database
# Easy (51.26%)
# Likes:    9
# Dislikes: 1
# Total Accepted:    4.2K
# Total Submissions: 8.1K
# Testcase Example:  "{\"headers\":{\"Triangles\":[\"A\",\"B\",\"C\"]},\"rows\":{\"Triangles\":[[20,20,23],[20,20,20],[20,21,22],[13,14,30]]}}"
#
#
# Table: Triangles
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | A           | int  |
# | B           | int  |
# | C           | int  |
# +-------------+------+
# (A, B, C) is the primary key for this table.
# Each row include the lengths of each of a triangle's three sides.
#
# Write a query to find the type of triangle. Output one of the following
# for each row:
#
# Equilateral: It's a triangle with 3 sides of equal length.
#
# Isosceles: It's a triangle with 2 sides of equal length.
#
# Scalene: It's a triangle with 3 sides of differing lengths.
#
# Not A Triangle: The given values of A, B, and C don't form a triangle.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Triangles table:
# +----+----+----+
# | A  | B  | C  |
# +----+----+----+
# | 20 | 20 | 23 |
# | 20 | 20 | 20 |
# | 20 | 21 | 22 |
# | 13 | 14 | 30 |
# +----+----+----+
# Output:
# +----------------+
# | triangle_type  |
# +----------------+
# | Isosceles      |
# | Equilateral    |
# | Scalene        |
# | Not A Triangle |
# +----------------+
# Explanation:
# - Values in the first row from an Isosceles triangle, because A = B.
# - Values in the second row from an Equilateral triangle, because A = B =
# C.
# - Values in the third row from an Scalene triangle, because A != B != C.
# - Values in the fourth row cannot form a triangle, because the combined
# value of sides A and B is not larger than that of side C.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Triangles(A, B, C). Classify each row as Equilateral,
        Isosceles, Scalene, or Not A Triangle.

        Algorithm:
        - CASE: triangle inequality first; then equality patterns among sides.

        Complexity: O(N).
        """
        self.sql = """
SELECT
    CASE
        WHEN A + B <= C OR A + C <= B OR B + C <= A THEN 'Not A Triangle'
        WHEN A = B AND B = C THEN 'Equilateral'
        WHEN A = B OR B = C OR A = C THEN 'Isosceles'
        ELSE 'Scalene'
    END AS triangle_type
FROM Triangles;
"""
        return self.sql
# @lc code=end

