#
# @lc app=leetcode id=2132 lang=python3
#
# [2132] Stamping the Grid
#
# https://leetcode.com/problems/stamping-the-grid/description/
#
# algorithms
# Hard (35.60%)
# Likes:    423
# Dislikes: 47
# Total Accepted:    10.7K
# Total Submissions: 29.9K
# Testcase Example:  "[[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]]\n4\n3"
#
# You are given an m x n binary matrix grid where each cell is either 0 (empty)
# or 1 (occupied).
#
# You are then given stamps of size stampHeight x stampWidth. We want to fit the
# stamps such that they follow the given restrictions and requirements:
#
#
# Cover all the empty cells.
#
#
# Do not cover any of the occupied cells.
#
#
# We can put as many stamps as we want.
#
#
# Stamps can overlap with each other.
#
#
# Stamps are not allowed to be rotated.
#
#
# Stamps must stay completely inside the grid.
#
# Return true if it is possible to fit the stamps while following the given
# restrictions and requirements. Otherwise, return false.
#
#
#
# Example 1:
#
# Input: grid = [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]], stampHeight
# = 4, stampWidth = 3
# Output: true
# Explanation: We have two overlapping stamps (labeled 1 and 2 in the image)
# that are able to cover all the empty cells.
#
# Example 2:
#
# Input: grid = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], stampHeight = 2,
# stampWidth = 2
# Output: false
# Explanation: There is no way to fit the stamps onto all the empty cells
# without the stamps going outside the grid.
#
#
#
# Constraints:
#
#
# m == grid.length
#
#
# n == grid[r].length
#
#
# 1 <= m, n <= 10^5
#
#
# 1 <= m * n <= 2 * 10^5
#
#
# grid[r][c] is either 0 or 1.
#
#
# 1 <= stampHeight, stampWidth <= 10^5
#


# @lc code=start
from typing import List


class Solution:
    def possibleToStamp(self, grid: List[List[int]], stampHeight: int, stampWidth: int) -> bool:
        """
        Interview explanation:
        Stamp h×w rectangles only on all-empty cells; stamps may overlap.
        Can every empty cell be covered by at least one stamp?

        Algorithm:
        - Prefix occupied counts; mark every top-left where stamp fits on empties.
        - 2D difference to compute coverage; every empty cell must be covered.

        Complexity: O(mn) time/space.
        """
        m, n = len(grid), len(grid[0])
        h, w = stampHeight, stampWidth
        pref = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m):
            for j in range(n):
                pref[i + 1][j + 1] = pref[i + 1][j] + pref[i][j + 1] - pref[i][j] + grid[i][j]

        def rect_sum(r1, c1, r2, c2) -> int:
            return pref[r2 + 1][c2 + 1] - pref[r1][c2 + 1] - pref[r2 + 1][c1] + pref[r1][c1]

        stamp = [[0] * n for _ in range(m)]
        for i in range(m - h + 1):
            for j in range(n - w + 1):
                if rect_sum(i, j, i + h - 1, j + w - 1) == 0:
                    stamp[i][j] = 1

        diff = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m - h + 1):
            for j in range(n - w + 1):
                if stamp[i][j]:
                    diff[i][j] += 1
                    diff[i][j + w] -= 1
                    diff[i + h][j] -= 1
                    diff[i + h][j + w] += 1

        cover = [[0] * n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                v = diff[i][j]
                if i:
                    v += cover[i - 1][j]
                if j:
                    v += cover[i][j - 1]
                if i and j:
                    v -= cover[i - 1][j - 1]
                cover[i][j] = v
                if grid[i][j] == 0 and cover[i][j] == 0:
                    return False
        return True
# @lc code=end

