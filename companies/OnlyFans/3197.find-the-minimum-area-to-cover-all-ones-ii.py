#
# @lc app=leetcode id=3197 lang=python3
#
# [3197] Find the Minimum Area to Cover All Ones II
#
# https://leetcode.com/problems/find-the-minimum-area-to-cover-all-ones-ii/description/
#
# algorithms
# Hard (63.53%)
# Likes:    403
# Dislikes: 69
# Total Accepted:    65.4K
# Total Submissions: 102.9K
# Testcase Example:  "[[1,0,1],[1,1,1]]"
#
#
# You are given a 2D binary array grid. You need to find 3 non-overlapping
# rectangles having non-zero areas with horizontal and vertical sides such
# that all the 1's in grid lie inside these rectangles.
#
# Return the minimum possible sum of the area of these rectangles.
#
# Note that the rectangles are allowed to touch.
#
# Example 1:
#
# Input: grid = [[1,0,1],[1,1,1]]
#
# Output: 5
#
# Explanation:
#
# The 1's at (0, 0) and (1, 0) are covered by a rectangle of area 2.
#
# The 1's at (0, 2) and (1, 2) are covered by a rectangle of area 2.
#
# The 1 at (1, 1) is covered by a rectangle of area 1.
#
# Example 2:
#
# Input: grid = [[1,0,1,0],[0,1,0,1]]
#
# Output: 5
#
# Explanation:
#
# The 1's at (0, 0) and (0, 2) are covered by a rectangle of area 3.
#
# The 1 at (1, 1) is covered by a rectangle of area 1.
#
# The 1 at (1, 3) is covered by a rectangle of area 1.
#
# Constraints:
#
# 1 <= grid.length, grid[i].length <= 30
#
# grid[i][j] is either 0 or 1.
#
# The input is generated such that there are at least three 1's in grid.
#

# @lc code=start

from typing import List
from math import inf


class Solution:
    def minimumSum(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Cover all 1s with 3 non-overlapping axis-aligned rectangles; minimize
        sum of areas. Enumerate the 6 partition topologies of a rectangle into 3.

        Algorithm:
        - Helper f(i1,j1,i2,j2): bounding-box area of 1s in that subgrid (inf if none).
        - Enumerate: 2 horizontal cuts, 2 vertical cuts, and T/L-shaped one-cut+split.

        Complexity: O(m^2 n^2) time (m,n<=30), O(1) extra space.
        """
        def area(i1: int, j1: int, i2: int, j2: int) -> int:
            x1 = y1 = inf
            x2 = y2 = -inf
            for i in range(i1, i2 + 1):
                for j in range(j1, j2 + 1):
                    if grid[i][j]:
                        x1 = min(x1, i)
                        y1 = min(y1, j)
                        x2 = max(x2, i)
                        y2 = max(y2, j)
            if x1 is inf:
                return inf
            return (x2 - x1 + 1) * (y2 - y1 + 1)

        m, n = len(grid), len(grid[0])
        ans = m * n

        for i1 in range(m - 1):
            for i2 in range(i1 + 1, m - 1):
                ans = min(
                    ans,
                    area(0, 0, i1, n - 1)
                    + area(i1 + 1, 0, i2, n - 1)
                    + area(i2 + 1, 0, m - 1, n - 1),
                )
        for j1 in range(n - 1):
            for j2 in range(j1 + 1, n - 1):
                ans = min(
                    ans,
                    area(0, 0, m - 1, j1)
                    + area(0, j1 + 1, m - 1, j2)
                    + area(0, j2 + 1, m - 1, n - 1),
                )
        for i in range(m - 1):
            for j in range(n - 1):
                ans = min(
                    ans,
                    area(0, 0, i, j) + area(0, j + 1, i, n - 1) + area(i + 1, 0, m - 1, n - 1),
                )
                ans = min(
                    ans,
                    area(0, 0, i, n - 1)
                    + area(i + 1, 0, m - 1, j)
                    + area(i + 1, j + 1, m - 1, n - 1),
                )
                ans = min(
                    ans,
                    area(0, 0, i, j) + area(i + 1, 0, m - 1, j) + area(0, j + 1, m - 1, n - 1),
                )
                ans = min(
                    ans,
                    area(0, 0, m - 1, j)
                    + area(0, j + 1, i, n - 1)
                    + area(i + 1, j + 1, m - 1, n - 1),
                )
        return ans
# @lc code=end
