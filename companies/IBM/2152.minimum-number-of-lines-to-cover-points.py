#
# @lc app=leetcode id=2152 lang=python3
#
# [2152] Minimum Number of Lines to Cover Points
#
# https://leetcode.com/problems/minimum-number-of-lines-to-cover-points/description/
#
# algorithms
# Medium (44.19%)
# Likes:    78
# Dislikes: 14
# Total Accepted:    2.9K
# Total Submissions: 6.6K
# Testcase Example:  "[[0,1],[2,3],[4,5],[4,3]]"
#
#
# You are given an array points where points[i] = [x_i, y_i] represents a
# point on an X-Y plane.
#
# Straight lines are going to be added to the X-Y plane, such that every
# point is covered by at least one line.
#
# Return the minimum number of straight lines needed to cover all the
# points.
#
# Example 1:
#
# Input: points = [[0,1],[2,3],[4,5],[4,3]]
# Output: 2
# Explanation: The minimum number of straight lines needed is two. One
# possible solution is to add:
# - One line connecting the point at (0, 1) to the point at (4, 5).
# - Another line connecting the point at (2, 3) to the point at (4, 3).
#
# Example 2:
#
# Input: points = [[0,2],[-2,-2],[1,4]]
# Output: 1
# Explanation: The minimum number of straight lines needed is one. The
# only solution is to add:
# - One line connecting the point at (-2, -2) to the point at (1, 4).
#
# Constraints:
#
# 1 <= points.length <= 10
#
# points[i].length == 2
#
# -100 <= x_i, y_i <= 100
#
# All the points are unique.
#
# @lc code=start
from typing import List
from functools import cache
from math import inf


class Solution:
    def minimumLines(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium. Cover all unique points with the fewest straight lines.
        n <= 10 → bitmask DP over covered subsets.

        Algorithm:
        (bitmask DP / DFS)
        - dfs(mask): min lines to cover remaining points.
        - Take first uncovered i; either cover alone, or pair with each j and
          cover all points collinear with (i,j) in one line.

        Complexity: O(3^n * n) roughly / O(2^n * n^2) with memo, O(2^n) space.
        """
        n = len(points)

        def collinear(i: int, j: int, k: int) -> bool:
            x1, y1 = points[i]
            x2, y2 = points[j]
            x3, y3 = points[k]
            return (x2 - x1) * (y3 - y1) == (x3 - x1) * (y2 - y1)

        @cache
        def dfs(mask: int) -> int:
            if mask == (1 << n) - 1:
                return 0
            i = 0
            while (mask >> i) & 1:
                i += 1
            ans = 1 + dfs(mask | (1 << i))
            for j in range(i + 1, n):
                if (mask >> j) & 1:
                    continue
                nxt = mask | (1 << i) | (1 << j)
                for k in range(n):
                    if collinear(i, j, k):
                        nxt |= 1 << k
                ans = min(ans, 1 + dfs(nxt))
            return ans

        return dfs(0)
# @lc code=end
