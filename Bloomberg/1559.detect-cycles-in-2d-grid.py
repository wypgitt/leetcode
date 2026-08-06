#
# @lc app=leetcode id=1559 lang=python3
#
# [1559] Detect Cycles in 2D Grid
#
# https://leetcode.com/problems/detect-cycles-in-2d-grid/description/
#
# algorithms
# Medium (63.49%)
# Likes:    1540
# Dislikes: 33
# Total Accepted:    146K
# Total Submissions: 230K
# Testcase Example:  "[[\"a\",\"a\",\"a\",\"a\"],[\"a\",\"b\",\"b\",\"a\"],[\"a\",\"b\",\"b\",\"a\"],[\"a\",\"a\",\"a\",\"a\"]]"
#
# Given a 2D array of characters grid of size m x n, you need to find if there
# exists any cycle consisting of the same value in grid.
#
# A cycle is a path of length 4 or more in the grid that starts and ends at the
# same cell. From a given cell, you can move to one of the cells adjacent to it
# - in one of the four directions (up, down, left, or right), if it has the
# same value of the current cell.
#
# Also, you cannot move to the cell that you visited in your last move. For
# example, the cycle (1, 1) -> (1, 2) -> (1, 1) is invalid because from (1, 2)
# we visited (1, 1) which was the last visited cell.
#
# Return true if any cycle of the same value exists in grid, otherwise, return
# false.
#
# Example 1:
#
# Input: grid =
# [["a","a","a","a"],["a","b","b","a"],["a","b","b","a"],["a","a","a","a"]]
# Output: true
# Explanation: There are two valid cycles shown in different colors in the
# image below:
#
# Example 2:
#
# Input: grid =
# [["c","c","c","a"],["c","d","c","c"],["c","c","e","c"],["f","c","c","c"]]
# Output: true
# Explanation: There is only one valid cycle highlighted in the image below:
#
# Example 3:
#
# Input: grid = [["a","b","b"],["b","z","b"],["b","b","a"]]
# Output: false
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 500
#
# grid consists only of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def containsCycle(self, grid: List[List[str]]) -> bool:
        """
        Interview explanation:
        Same-letter 4-connected cycle of length >= 4. DFS/BFS with parent: if
        revisit a same-letter cell that isn't the parent, a cycle exists.

        Algorithm (DFS parent):
        - visited[][]; for each unvisited cell DFS same char; if neighbor
          visited and != parent → True.

        Complexity: O(mn) time/space.
        """
        m, n = len(grid), len(grid[0])
        vis = [[False] * n for _ in range(m)]
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

        def dfs(r: int, c: int, pr: int, pc: int) -> bool:
            vis[r][c] = True
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < m and 0 <= nc < n) or grid[nr][nc] != grid[r][c]:
                    continue
                if vis[nr][nc]:
                    if (nr, nc) != (pr, pc):
                        return True
                elif dfs(nr, nc, r, c):
                    return True
            return False

        for i in range(m):
            for j in range(n):
                if not vis[i][j] and dfs(i, j, -1, -1):
                    return True
        return False

    def containsCycle_uf(self, grid: List[List[str]]) -> bool:
        """
        Interview explanation:
        Alternate Union-Find: process cells left-to-right/top-to-bottom; union
        with left/up same letter; if already same component → cycle.

        Algorithm:
        - parent[mn]; for each cell, for left/up same char: if find equal True
          else union.

        Complexity: O(mn α(mn)).
        """
        m, n = len(grid), len(grid[0])
        parent = list(range(m * n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> bool:
            ra, rb = find(a), find(b)
            if ra == rb:
                return False
            parent[rb] = ra
            return True

        for i in range(m):
            for j in range(n):
                id_ = i * n + j
                if i > 0 and grid[i][j] == grid[i - 1][j]:
                    if not union(id_, (i - 1) * n + j):
                        return True
                if j > 0 and grid[i][j] == grid[i][j - 1]:
                    if not union(id_, i * n + j - 1):
                        return True
        return False
# @lc code=end

