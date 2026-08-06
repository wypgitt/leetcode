#
# @lc app=leetcode id=1001 lang=python3
#
# [1001] Grid Illumination
#
# https://leetcode.com/problems/grid-illumination/description/
#
# algorithms
# Hard (39.82%)
# Likes:    658
# Dislikes: 161
# Total Accepted:    28.4K
# Total Submissions: 71.3K
# Testcase Example:  "5"
#
# There is a 2D grid of size n x n where each cell of this grid has a lamp that
# is initially turned off.
#
# You are given a 2D array of lamp positions lamps, where lamps[i] = [row_i,
# col_i] indicates that the lamp at grid[row_i][col_i] is turned on. Even if
# the same lamp is listed more than once, it is turned on.
#
# When a lamp is turned on, it illuminates its cell and all other cells in the
# same row, column, or diagonal.
#
# You are also given another 2D array queries, where queries[j] = [row_j,
# col_j]. For the j^th query, determine whether grid[row_j][col_j] is
# illuminated or not. After answering the j^th query, turn off the lamp at
# grid[row_j][col_j] and its 8 adjacent lamps if they exist. A lamp is adjacent
# if its cell shares either a side or corner with grid[row_j][col_j].
#
# Return an array of integers ans, where ans[j] should be 1 if the cell in the
# j^th query was illuminated, or 0 if the lamp was not.
#
# Example 1:
#
# Input: n = 5, lamps = [[0,0],[4,4]], queries = [[1,1],[1,0]]
# Output: [1,0]
# Explanation: We have the initial grid with all lamps turned off. In the above
# picture we see the grid after turning on the lamp at grid[0][0] then turning
# on the lamp at grid[4][4].
# The 0^th query asks if the lamp at grid[1][1] is illuminated or not (the blue
# square). It is illuminated, so set ans[0] = 1. Then, we turn off all lamps in
# the red square.
#
# The 1^st query asks if the lamp at grid[1][0] is illuminated or not (the blue
# square). It is not illuminated, so set ans[1] = 0. Then, we turn off all
# lamps in the red rectangle.
#
# Example 2:
#
# Input: n = 5, lamps = [[0,0],[4,4]], queries = [[1,1],[1,1]]
# Output: [1,1]
#
# Example 3:
#
# Input: n = 5, lamps = [[0,0],[0,4]], queries = [[0,4],[0,1],[1,4]]
# Output: [1,1,0]
#
# Constraints:
#
# 1 <= n <= 10^9
#
# 0 <= lamps.length <= 20000
#
# 0 <= queries.length <= 20000
#
# lamps[i].length == 2
#
# 0 <= row_i, col_i < n
#
# queries[j].length == 2
#
# 0 <= row_j, col_j < n
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def gridIllumination(self, n: int, lamps: List[List[int]], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        n can be 1e9, so we cannot build the grid. Track illuminated rows, cols,
        and both diagonals with counters; store active lamp positions in a set.
        For each query, check if any of those lines are lit, then turn off the
        9-neighborhood lamps and decrement counters.

        Algorithm:
        - Dedup lamps into set; count rows, cols, diag (r-c), antidiag (r+c)
        - For each query (r,c): ans=1 if any counter >0 else 0
        - Turn off lamps in [r-1..r+1] x [c-1..c+1] present in set; update counts

        Complexity: O(L + Q) time, O(L) space.
        """
        lamp_set = {(r, c) for r, c in lamps}
        rows = defaultdict(int)
        cols = defaultdict(int)
        diag = defaultdict(int)
        anti = defaultdict(int)
        for r, c in lamp_set:
            rows[r] += 1
            cols[c] += 1
            diag[r - c] += 1
            anti[r + c] += 1

        def turn_off(r: int, c: int) -> None:
            if (r, c) not in lamp_set:
                return
            lamp_set.remove((r, c))
            rows[r] -= 1
            cols[c] -= 1
            diag[r - c] -= 1
            anti[r + c] -= 1

        ans = []
        for r, c in queries:
            lit = rows[r] > 0 or cols[c] > 0 or diag[r - c] > 0 or anti[r + c] > 0
            ans.append(1 if lit else 0)
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < n:
                        turn_off(nr, nc)
        return ans
# @lc code=end
