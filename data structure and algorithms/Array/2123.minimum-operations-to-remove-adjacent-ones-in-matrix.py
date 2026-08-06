#
# @lc app=leetcode id=2123 lang=python3
#
# [2123] Minimum Operations to Remove Adjacent Ones in Matrix
#
# https://leetcode.com/problems/minimum-operations-to-remove-adjacent-ones-in-matrix/description/
#
# algorithms
# Hard (43.58%)
# Likes:    55
# Dislikes: 13
# Total Accepted:    1.4K
# Total Submissions: 3.1K
# Testcase Example:  "[[1,1,0],[0,1,1],[1,1,1]]"
#
#
# You are given a 0-indexed binary matrix grid. In one operation, you can
# flip any 1 in grid to be 0.
#
# A binary matrix is well-isolated if there is no 1 in the matrix that is
# 4-directionally connected (i.e., horizontal and vertical) to another 1.
#
# Return the minimum number of operations to make grid well-isolated.
#
# Example 1:
#
# Input: grid = [[1,1,0],[0,1,1],[1,1,1]]
# Output: 3
# Explanation: Use 3 operations to change grid[0][1], grid[1][2], and
# grid[2][1] to 0.
# After, no more 1's are 4-directionally connected and grid is
# well-isolated.
#
# Example 2:
#
# Input: grid = [[0,0,0],[0,0,0],[0,0,0]]
# Output: 0
# Explanation: There are no 1's in grid and it is well-isolated.
# No operations were done so return 0.
#
# Example 3:
#
# Input: grid = [[0,1],[1,0]]
# Output: 0
# Explanation: None of the 1's are 4-directionally connected and grid is
# well-isolated.
# No operations were done so return 0.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 300
#
# grid[i][j] is either 0 or 1.
#
# @lc code=start
from typing import List


class Solution:
    def minimumOperations(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium: flip 1→0 min times so no two 1s are 4-adjacent (well-isolated).
        Chessboard bipartite graph of 1-cells; min flips = min vertex cover =
        maximum matching (König).

        Algorithm:
        - Left = cells with (i+j) even that are 1; edges to adjacent 1s.
        - DFS augmenting paths; answer = matching size.

        Complexity: O(V*E) with DFS matching; V,E ≤ O(mn).
        """
        m, n = len(grid), len(grid[0])
        match = {}  # right cell -> left cell

        def neighbors(i, j):
            for di, dj in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                x, y = i + di, j + dj
                if 0 <= x < m and 0 <= y < n and grid[x][y] == 1:
                    yield (x, y)

        def dfs(u, seen) -> bool:
            for v in neighbors(*u):
                if v in seen:
                    continue
                seen.add(v)
                if v not in match or dfs(match[v], seen):
                    match[v] = u
                    return True
            return False

        ans = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] == 1 and (i + j) % 2 == 0:
                    if dfs((i, j), set()):
                        ans += 1
        return ans
# @lc code=end

