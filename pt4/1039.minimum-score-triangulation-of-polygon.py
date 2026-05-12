#
# @lc app=leetcode id=1039 lang=python3
#
# [1039] Minimum Score Triangulation of Polygon
#
# https://leetcode.com/problems/minimum-score-triangulation-of-polygon/description/
#
# algorithms
# Medium (67.44%)
# Likes:    2328
# Dislikes: 304
# Total Accepted:    141.7K
# Total Submissions: 210.1K
# Testcase Example:  '[1,2,3]'
#
# You have a convex n-sided polygon where each vertex has an integer value. You
# are given an integer array values where values[i] is the value of the i^th
# vertex in clockwise order.
# 
# Polygon triangulation is a process where you divide a polygon into a set of
# triangles and the vertices of each triangle must also be vertices of the
# original polygon. Note that no other shapes other than triangles are allowed
# in the division. This process will result in n - 2 triangles.
# 
# You will triangulate the polygon. For each triangle, the weight of that
# triangle is the product of the values at its vertices. The total score of the
# triangulation is the sum of these weights over all n - 2 triangles.
# 
# Return the minimum possible score that you can achieve with some
# triangulation of the polygon.
# 
# 
# 
# Example 1:
# 
# 
# 
# 
# Input: values = [1,2,3]
# 
# Output: 6
# 
# Explanation: The polygon is already triangulated, and the score of the only
# triangle is 6.
# 
# 
# Example 2:
# 
# 
# 
# 
# Input: values = [3,7,4,5]
# 
# Output: 144
# 
# Explanation: There are two triangulations, with possible scores: 3*7*5 +
# 4*5*7 = 245, or 3*4*5 + 3*4*7 = 144.
# The minimum score is 144.
# 
# 
# Example 3:
# 
# ​​​​​​​
# 
# 
# Input: values = [1,3,1,4,1,5]
# 
# Output: 13
# 
# Explanation: The minimum score triangulation is 1*1*3 + 1*1*4 + 1*1*5 + 1*1*1
# = 13.
# 
# 
# 
# Constraints:
# 
# 
# n == values.length
# 3 <= n <= 50
# 1 <= values[i] <= 100
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def minScoreTriangulation(self, values: List[int]) -> int:
        n = len(values)
        dp = [[0] * n for _ in range(n)]

        for gap in range(2, n):
            for left in range(n - gap):
                right = left + gap
                dp[left][right] = min(
                    dp[left][mid]
                    + dp[mid][right]
                    + values[left] * values[mid] * values[right]
                    for mid in range(left + 1, right)
                )

        return dp[0][n - 1]
# @lc code=end

"""
Interview Explanation

Core idea:
Choose one triangle that uses an edge between two boundary vertices left and
right. Its third vertex mid splits the polygon interval into two independent
smaller polygons.

Algorithm:
Let dp[left][right] be the minimum triangulation score for the polygon chain
from left to right.
- If fewer than 3 vertices are in the interval, score is 0.
- Otherwise, try every possible mid between left and right as the triangle
  (left, mid, right).
- Combine left subproblem, right subproblem, and the triangle product.
Fill intervals by increasing length so subproblems are ready first.

Data structure choice:
A 2D interval DP table directly represents sub-polygons. This is the standard
structure for "split an interval and combine both sides" problems.

Correctness:
Every triangulation of interval [left, right] contains exactly one triangle
using edge (left, right), with some third vertex mid. Removing that triangle
leaves two independent intervals. The recurrence tries every possible mid and
uses optimal scores for both smaller intervals, so it considers every
triangulation and chooses the minimum.

Complexity:
There are O(n^2) intervals and O(n) choices of mid per interval, so time is
O(n^3). Space is O(n^2).

Tests and edge cases:
- n = 3: one triangle, product of all values.
- n = 4: chooses the cheaper of the two diagonals.
- Repeated small values: DP still evaluates all splits.
- Maximum n = 50 is fine for O(n^3).
"""
