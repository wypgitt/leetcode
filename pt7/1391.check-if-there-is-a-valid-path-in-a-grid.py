#
# @lc app=leetcode id=1391 lang=python3
#
# [1391] Check if There is a Valid Path in a Grid
#
# https://leetcode.com/problems/check-if-there-is-a-valid-path-in-a-grid/description/
#
# algorithms
# Medium (64.45%)
# Likes:    1064
# Dislikes: 348
# Total Accepted:    106.3K
# Total Submissions: 164.8K
# Testcase Example:  '[[2,4,3],[6,5,2]]'
#
# You are given an m x n grid. Each cell of grid represents a street. The
# street of grid[i][j] can be:
# 
# 
# 1 which means a street connecting the left cell and the right cell.
# 2 which means a street connecting the upper cell and the lower cell.
# 3 which means a street connecting the left cell and the lower cell.
# 4 which means a street connecting the right cell and the lower cell.
# 5 which means a street connecting the left cell and the upper cell.
# 6 which means a street connecting the right cell and the upper cell.
# 
# 
# You will initially start at the street of the upper-left cell (0, 0). A valid
# path in the grid is a path that starts from the upper left cell (0, 0) and
# ends at the bottom-right cell (m - 1, n - 1). The path should only follow the
# streets.
# 
# Notice that you are not allowed to change any street.
# 
# Return true if there is a valid path in the grid or false otherwise.
# 
# 
# Example 1:
# 
# 
# Input: grid = [[2,4,3],[6,5,2]]
# Output: true
# Explanation: As shown you can start at cell (0, 0) and visit all the cells of
# the grid to reach (m - 1, n - 1).
# 
# 
# Example 2:
# 
# 
# Input: grid = [[1,2,1],[1,2,1]]
# Output: false
# Explanation: As shown you the street at cell (0, 0) is not connected with any
# street of any other cell and you will get stuck at cell (0, 0)
# 
# 
# Example 3:
# 
# 
# Input: grid = [[1,1,2]]
# Output: false
# Explanation: You will get stuck at cell (0, 1) and you cannot reach cell (0,
# 2).
# 
# 
# 
# Constraints:
# 
# 
# m == grid.length
# n == grid[i].length
# 1 <= m, n <= 300
# 1 <= grid[i][j] <= 6
# 
# 
#

# @lc code=start
from __future__ import annotations

from collections import deque
from typing import List


class Solution:
    def hasValidPath(self, grid: List[List[int]]) -> bool:
        directions = {
            1: [(0, -1), (0, 1)],
            2: [(-1, 0), (1, 0)],
            3: [(0, -1), (1, 0)],
            4: [(0, 1), (1, 0)],
            5: [(0, -1), (-1, 0)],
            6: [(0, 1), (-1, 0)],
        }

        rows, cols = len(grid), len(grid[0])
        queue = deque([(0, 0)])
        seen = {(0, 0)}

        while queue:
            row, col = queue.popleft()
            if row == rows - 1 and col == cols - 1:
                return True

            for dr, dc in directions[grid[row][col]]:
                next_row = row + dr
                next_col = col + dc

                if not (0 <= next_row < rows and 0 <= next_col < cols):
                    continue
                if (next_row, next_col) in seen:
                    continue
                if (-dr, -dc) not in directions[grid[next_row][next_col]]:
                    continue

                seen.add((next_row, next_col))
                queue.append((next_row, next_col))

        return False
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Each grid cell is a graph node, and its street type defines which neighboring
# cells it can connect to. A move is valid only if the current cell has an exit
# in that direction and the neighbor has a matching entrance back.
#
# Data structure:
# - A dictionary maps street type to allowed direction deltas.
# - BFS queue explores reachable cells.
# - `seen` prevents cycles.
#
# Walkthrough:
# 1. Start BFS from `(0, 0)`.
# 2. For each allowed direction from the current street, compute the neighbor.
# 3. Reject out-of-bounds or already visited neighbors.
# 4. Check that the neighbor's street includes the opposite direction.
# 5. If bottom-right is reached, return True.
#
# Edge cases:
# - 1x1 grid: start is destination, so return True.
# - One-way mismatch: rejected by the opposite-direction check.
# - Cycles in streets: `seen` prevents infinite BFS.
#
# Complexity:
# - Time: O(mn), each cell is visited at most once.
# - Space: O(mn), for BFS and visited set.
