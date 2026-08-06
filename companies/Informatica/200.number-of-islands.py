"""
Approach: Flood-fill each unvisited land component.
Data structure: an explicit stack performs DFS and mutates visited land to water to avoid a separate visited set.
Interview logic: every time we find a '1', it starts one island. DFS marks all land connected to it, so no cell from that island is counted again.
Complexity: O(mn) time, O(mn) worst-case stack space.
Tests and edge cases: empty grid returns 0; all water returns 0; diagonal adjacency does not connect islands.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        if not grid or not grid[0]:
            return 0
        rows, cols = len(grid), len(grid[0])
        islands = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != '1':
                    continue
                islands += 1
                grid[r][c] = '0'
                stack = [(r, c)]
                while stack:
                    x, y = stack.pop()
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == '1':
                            grid[nx][ny] = '0'
                            stack.append((nx, ny))
        return islands
# @lc code=end
