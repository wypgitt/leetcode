#
# @lc app=leetcode id=711 lang=python3
#
# [711] Number of Distinct Islands II
#
# https://leetcode.com/problems/number-of-distinct-islands-ii/description/
#
# algorithms
# Hard (55.58%)
# Likes:    282
# Dislikes: 286
# Total Accepted:    14.5K
# Total Submissions: 26.1K
# Testcase Example:  "[[1,1,0,0,0],[1,0,0,0,0],[0,0,0,0,1],[0,0,0,1,1]]"
#
#
# You are given an m x n binary matrix grid. An island is a group of 1's
# (representing land) connected 4-directionally (horizontal or vertical.)
# You may assume all four edges of the grid are surrounded by water.
#
# An island is considered to be the same as another if they have the same
# shape, or have the same shape after rotation (90, 180, or 270 degrees
# only) or reflection (left/right direction or up/down direction).
#
# Return the number of distinct islands.
#
# Example 1:
#
# Input: grid = [[1,1,0,0,0],[1,0,0,0,0],[0,0,0,0,1],[0,0,0,1,1]]
# Output: 1
# Explanation: The two islands are considered the same because if we make
# a 180 degrees clockwise rotation on the first island, then two islands
# will have the same shapes.
#
# Example 2:
#
# Input: grid = [[1,1,0,0,0],[1,1,0,0,0],[0,0,0,1,1],[0,0,0,1,1]]
# Output: 1
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 50
#
# grid[i][j] is either 0 or 1.
#
# @lc code=start
from typing import List, Tuple


class Solution:
    def numDistinctIslands2(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium: distinct islands under translation, rotation, and reflection.
        Collect cells of each island; generate all 8 dihedral transforms;
        normalize each (translate so min is (0,0), sort); take canonical min
        signature into a set.

        Algorithm:
        - DFS gather relative coordinates.
        - For shapes: for (x,y) in cells produce (x,y),(x,-y),(-x,y),(-x,-y),
          (y,x),(y,-x),(-y,x),(-y,-x); normalize; frozenset of sorted tuples.
        - Canonical = min of 8 normalized forms (as tuple).

        Complexity: O(m*n * s log s) with s island size, O(m*n) space.
        """
        if not grid:
            return 0
        m, n = len(grid), len(grid[0])

        def dfs(i: int, j: int, cells: List[Tuple[int, int]]) -> None:
            if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] == 0:
                return
            grid[i][j] = 0
            cells.append((i, j))
            dfs(i + 1, j, cells)
            dfs(i - 1, j, cells)
            dfs(i, j + 1, cells)
            dfs(i, j - 1, cells)

        def normalize(shape: List[Tuple[int, int]]) -> Tuple[Tuple[int, int], ...]:
            shapes = []
            for k in range(8):
                transformed = []
                for x, y in shape:
                    if k == 0:
                        nx, ny = x, y
                    elif k == 1:
                        nx, ny = x, -y
                    elif k == 2:
                        nx, ny = -x, y
                    elif k == 3:
                        nx, ny = -x, -y
                    elif k == 4:
                        nx, ny = y, x
                    elif k == 5:
                        nx, ny = y, -x
                    elif k == 6:
                        nx, ny = -y, x
                    else:
                        nx, ny = -y, -x
                    transformed.append((nx, ny))
                minx = min(p[0] for p in transformed)
                miny = min(p[1] for p in transformed)
                norm = sorted((p[0] - minx, p[1] - miny) for p in transformed)
                shapes.append(tuple(norm))
            return min(shapes)

        seen = set()
        for i in range(m):
            for j in range(n):
                if grid[i][j] == 1:
                    cells: List[Tuple[int, int]] = []
                    dfs(i, j, cells)
                    seen.add(normalize(cells))
        return len(seen)
# @lc code=end
