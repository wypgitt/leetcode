#
# @lc app=leetcode id=1659 lang=python3
#
# [1659] Maximize Grid Happiness
#
# https://leetcode.com/problems/maximize-grid-happiness/description/
#
# algorithms
# Hard (41.37%)
# Likes:    347
# Dislikes: 56
# Total Accepted:    7.9K
# Total Submissions: 19.0K
# Testcase Example:  "2"
#
# You are given four integers, m, n, introvertsCount, and extrovertsCount. You
# have an m x n grid, and there are two types of people: introverts and
# extroverts. There are introvertsCount introverts and extrovertsCount
# extroverts.
#
# You should decide how many people you want to live in the grid and assign
# each of them one grid cell. Note that you do not have to have all the people
# living in the grid.
#
# The happiness of each person is calculated as follows:
#
# Introverts start with 120 happiness and lose 30 happiness for each neighbor
# (introvert or extrovert).
#
# Extroverts start with 40 happiness and gain 20 happiness for each neighbor
# (introvert or extrovert).
#
# Neighbors live in the directly adjacent cells north, east, south, and west of
# a person's cell.
#
# The grid happiness is the sum of each person's happiness. Return the maximum
# possible grid happiness.
#
# Example 1:
#
# Input: m = 2, n = 3, introvertsCount = 1, extrovertsCount = 2
# Output: 240
# Explanation: Assume the grid is 1-indexed with coordinates (row, column).
# We can put the introvert in cell (1,1) and put the extroverts in cells (1,3)
# and (2,3).
# - Introvert at (1,1) happiness: 120 (starting happiness) - (0 * 30) (0
# neighbors) = 120
# - Extrovert at (1,3) happiness: 40 (starting happiness) + (1 * 20) (1
# neighbor) = 60
# - Extrovert at (2,3) happiness: 40 (starting happiness) + (1 * 20) (1
# neighbor) = 60
# The grid happiness is 120 + 60 + 60 = 240.
# The above figure shows the grid in this example with each person's happiness.
# The introvert stays in the light green cell while the extroverts live on the
# light purple cells.
#
# Example 2:
#
# Input: m = 3, n = 1, introvertsCount = 2, extrovertsCount = 1
# Output: 260
# Explanation: Place the two introverts in (1,1) and (3,1) and the extrovert at
# (2,1).
# - Introvert at (1,1) happiness: 120 (starting happiness) - (1 * 30) (1
# neighbor) = 90
# - Extrovert at (2,1) happiness: 40 (starting happiness) + (2 * 20) (2
# neighbors) = 80
# - Introvert at (3,1) happiness: 120 (starting happiness) - (1 * 30) (1
# neighbor) = 90
# The grid happiness is 90 + 80 + 90 = 260.
#
# Example 3:
#
# Input: m = 2, n = 2, introvertsCount = 4, extrovertsCount = 0
# Output: 240
#
# Constraints:
#
# 1 <= m, n <= 5
#
# 0 <= introvertsCount, extrovertsCount <= min(m * n, 6)
#

# @lc code=start
from functools import lru_cache


class Solution:
    def getMaxGridHappiness(self, m: int, n: int, introvertsCount: int, extrovertsCount: int) -> int:
        """
        Interview explanation:
        Place introverts/extroverts on m×n grid (m<=5,n<=5) maximizing happiness.
        Introvert: +120, -30 per neighbor; Extrovert: +40, +20 per neighbor.
        DP over rows with ternary mask of previous row occupancy.

        Algorithm (row DP / bit DP):
        - Encode cell: 0 empty, 1 intro, 2 extro; masks base-3 of width n.
        - dfs(pos, introLeft, extroLeft, prevMask) placing left-to-right, top-down.
        - Add happiness deltas vs left neighbor and up neighbor.

        Complexity: O(m*n * 3^n * I * E) with memo; small constants.
        """
        N = n
        total = m * n
        # precompute base-3 powers
        pow3 = [1] * (N + 1)
        for i in range(N):
            pow3[i + 1] = pow3[i] * 3

        def get(mask, j):
            return (mask // pow3[j]) % 3

        def setv(mask, j, v):
            return mask + (v - get(mask, j)) * pow3[j]

        @lru_cache(None)
        def dfs(pos, inLeft, exLeft, prev):
            if pos == total or (inLeft == 0 and exLeft == 0):
                return 0
            r, c = divmod(pos, N)
            # next-row mask: when c==0, prev is previous row; we build cur row mask
            # Represent prev as mask of previous n cells (row above for current).
            best = dfs(pos + 1, inLeft, exLeft, setv(prev, c, 0))  # leave empty
            up = get(prev, c)
            left = get(prev, c - 1) if c > 0 else 0

            def delta(t, neigh_t):
                if t == 0 or neigh_t == 0:
                    return 0
                # mutual neighbor cost/gain
                d = 0
                d += -30 if t == 1 else 20
                d += -30 if neigh_t == 1 else 20
                return d

            if inLeft:
                add = 120
                add += delta(1, up) + delta(1, left)
                best = max(best, add + dfs(pos + 1, inLeft - 1, exLeft, setv(prev, c, 1)))
            if exLeft:
                add = 40
                add += delta(2, up) + delta(2, left)
                best = max(best, add + dfs(pos + 1, inLeft, exLeft - 1, setv(prev, c, 2)))
            return best

        return dfs(0, introvertsCount, extrovertsCount, 0)
# @lc code=end
