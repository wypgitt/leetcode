#
# @lc app=leetcode id=803 lang=python3
#
# [803] Bricks Falling When Hit
#
# https://leetcode.com/problems/bricks-falling-when-hit/description/
#
# algorithms
# Hard (37.64%)
# Likes:    1217
# Dislikes: 194
# Total Accepted:    39.7K
# Total Submissions: 106K
# Testcase Example:  "[[1,0,0,0],[1,1,1,0]]"
#
# You are given an m x n binary grid, where each 1 represents a brick and 0
# represents an empty space. A brick is stable if:
#
# It is directly connected to the top of the grid, or
#
# At least one other brick in its four adjacent cells is stable.
#
# You are also given an array hits, which is a sequence of erasures we want to
# apply. Each time we want to erase the brick at the location hits[i] = (row_i,
# col_i). The brick on that location (if it exists) will disappear. Some other
# bricks may no longer be stable because of that erasure and will fall. Once a
# brick falls, it is immediately erased from the grid (i.e., it does not land
# on other stable bricks).
#
# Return an array result, where each result[i] is the number of bricks that
# will fall after the i^th erasure is applied.
#
# Note that an erasure may refer to a location with no brick, and if it does,
# no bricks drop.
#
# Example 1:
#
# Input: grid = [[1,0,0,0],[1,1,1,0]], hits = [[1,0]]
# Output: [2]
# Explanation: Starting with the grid:
# [[1,0,0,0],
# [1,1,1,0]]
# We erase the underlined brick at (1,0), resulting in the grid:
# [[1,0,0,0],
# [0,1,1,0]]
# The two underlined bricks are no longer stable as they are no longer
# connected to the top nor adjacent to another stable brick, so they will fall.
# The resulting grid is:
# [[1,0,0,0],
# [0,0,0,0]]
# Hence the result is [2].
#
# Example 2:
#
# Input: grid = [[1,0,0,0],[1,1,0,0]], hits = [[1,1],[1,0]]
# Output: [0,0]
# Explanation: Starting with the grid:
# [[1,0,0,0],
# [1,1,0,0]]
# We erase the underlined brick at (1,1), resulting in the grid:
# [[1,0,0,0],
# [1,0,0,0]]
# All remaining bricks are still stable, so no bricks fall. The grid remains
# the same:
# [[1,0,0,0],
# [1,0,0,0]]
# Next, we erase the underlined brick at (1,0), resulting in the grid:
# [[1,0,0,0],
# [0,0,0,0]]
# Once again, all remaining bricks are still stable, so no bricks fall.
# Hence the result is [0,0].
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 200
#
# grid[i][j] is 0 or 1.
#
# 1 <= hits.length <= 4 * 10^4
#
# hits[i].length == 2
#
# 0 <= x_i <= m - 1
#
# 0 <= y_i <= n - 1
#
# All (x_i, y_i) are unique.
#

# @lc code=start

from typing import List


class Solution:
    def hitBricks(self, grid: List[List[int]], hits: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Reverse Union-Find: apply all hits first (erase bricks), union remaining
        bricks to a virtual roof node, then add hits back in reverse. Each added
        brick that connects newly to the roof causes (new_roof_size - old - 1)
        bricks to "fall restored" — that count is the answer for that hit.

        Algorithm (reverse UF):
        - Copy grid; erase hit cells (mark 0 if was 1).
        - UF with node R = m*n as roof; union adjacent 1s; row0 union roof.
        - Process hits reversed: if cell was brick, place it, union neighbors,
          ans = max(0, size(roof)-prev-1).

        Complexity: O((mn + hits) α(mn)) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        R = m * n
        parent = list(range(R + 1))
        size = [1] * (R + 1)

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if size[ra] < size[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            size[ra] += size[rb]

        def idx(i: int, j: int) -> int:
            return i * n + j

        g = [row[:] for row in grid]
        for x, y in hits:
            g[x][y] -= 1  # may go -1 if empty hit

        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

        def neighbors(i: int, j: int):
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n and g[ni][nj] == 1:
                    yield ni, nj

        for i in range(m):
            for j in range(n):
                if g[i][j] != 1:
                    continue
                if i == 0:
                    union(idx(i, j), R)
                for ni, nj in neighbors(i, j):
                    union(idx(i, j), idx(ni, nj))

        ans = [0] * len(hits)
        for t in range(len(hits) - 1, -1, -1):
            x, y = hits[t]
            g[x][y] += 1
            if g[x][y] != 1:
                continue
            prev = size[find(R)]
            if x == 0:
                union(idx(x, y), R)
            for ni, nj in neighbors(x, y):
                union(idx(x, y), idx(ni, nj))
            cur = size[find(R)]
            ans[t] = max(0, cur - prev - 1)
        return ans
# @lc code=end
