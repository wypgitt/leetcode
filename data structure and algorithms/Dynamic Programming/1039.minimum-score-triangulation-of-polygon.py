#
# @lc app=leetcode id=1039 lang=python3
#
# [1039] Minimum Score Triangulation of Polygon
#
# https://leetcode.com/problems/minimum-score-triangulation-of-polygon/description/
#
# algorithms
# Medium (67.58%)
# Likes:    2345
# Dislikes: 304
# Total Accepted:    145K
# Total Submissions: 214K
# Testcase Example:  "[1,2,3]"
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
# Example 1:
#
# Input: values = [1,2,3]
#
# Output: 6
#
# Explanation: The polygon is already triangulated, and the score of the only
# triangle is 6.
#
# Example 2:
#
# Input: values = [3,7,4,5]
#
# Output: 144
#
# Explanation: There are two triangulations, with possible scores: 3*7*5 +
# 4*5*7 = 245, or 3*4*5 + 3*4*7 = 144.
#
# The minimum score is 144.
#
# Example 3:
#
# Input: values = [1,3,1,4,1,5]
#
# Output: 13
#
# Explanation: The minimum score triangulation is 1*1*3 + 1*1*4 + 1*1*5 + 1*1*1
# = 13.
#
# Constraints:
#
# n == values.length
#
# 3 <= n <= 50
#
# 1 <= values[i] <= 100
#

# @lc code=start
from functools import lru_cache
from typing import List


class Solution:
    def minScoreTriangulation(self, values: List[int]) -> int:
        """
        Interview explanation:
        Interval DP on polygon vertices. For interval (i,j), try each k as the
        third vertex of the triangle with edge i-j: cost = v[i]*v[k]*v[j] +
        dp(i,k)+dp(k,j). Minimize over k.

        Algorithm:
        - dp[i][j]=0 for j=i+1; for length>=2: min over k

        Complexity: O(n^3) time, O(n^2) space.
        """
        n = len(values)
        dp = [[0] * n for _ in range(n)]
        for length in range(2, n):
            for i in range(n - length):
                j = i + length
                best = float("inf")
                for k in range(i + 1, j):
                    best = min(best, dp[i][k] + dp[k][j] + values[i] * values[k] * values[j])
                dp[i][j] = best
        return dp[0][n - 1]

    def minScoreTriangulation_memo(self, values: List[int]) -> int:
        """
        Interview explanation:
        Alternate top-down memoized recursion of the same interval DP.

        Algorithm:
        - dfs(i,j): if j==i+1: 0; else min over k of product + dfs(i,k)+dfs(k,j)

        Complexity: O(n^3) time, O(n^2) space.
        """
        @lru_cache(None)
        def dfs(i: int, j: int) -> int:
            if j <= i + 1:
                return 0
            best = float("inf")
            for k in range(i + 1, j):
                best = min(best, dfs(i, k) + dfs(k, j) + values[i] * values[k] * values[j])
            return best

        return dfs(0, len(values) - 1)
# @lc code=end
