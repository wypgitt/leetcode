#
# @lc app=leetcode id=2850 lang=python3
#
# [2850] Minimum Moves to Spread Stones Over Grid
#
# https://leetcode.com/problems/minimum-moves-to-spread-stones-over-grid/description/
#
# algorithms
# Medium (45.61%)
# Likes:    563
# Dislikes: 78
# Total Accepted:    31.1K
# Total Submissions: 68.3K
# Testcase Example:  "[[1,1,0],[1,1,1],[1,2,1]]"
#
#
# You are given a 0-indexed 2D integer matrix grid of size 3 * 3,
# representing the number of stones in each cell. The grid contains
# exactly 9 stones, and there can be multiple stones in a single cell.
#
# In one move, you can move a single stone from its current cell to any
# other cell if the two cells share a side.
#
# Return the minimum number of moves required to place one stone in each
# cell.
#
# Example 1:
#
# Input: grid = [[1,1,0],[1,1,1],[1,2,1]]
# Output: 3
# Explanation: One possible sequence of moves to place one stone in each
# cell is:
# 1- Move one stone from cell (2,1) to cell (2,2).
# 2- Move one stone from cell (2,2) to cell (1,2).
# 3- Move one stone from cell (1,2) to cell (0,2).
# In total, it takes 3 moves to place one stone in each cell of the grid.
# It can be shown that 3 is the minimum number of moves required to place
# one stone in each cell.
#
# Example 2:
#
# Input: grid = [[1,3,0],[1,0,0],[1,0,3]]
# Output: 4
# Explanation: One possible sequence of moves to place one stone in each
# cell is:
# 1- Move one stone from cell (0,1) to cell (0,2).
# 2- Move one stone from cell (0,1) to cell (1,1).
# 3- Move one stone from cell (2,2) to cell (1,2).
# 4- Move one stone from cell (2,2) to cell (2,1).
# In total, it takes 4 moves to place one stone in each cell of the grid.
# It can be shown that 4 is the minimum number of moves required to place
# one stone in each cell.
#
# Constraints:
#
# grid.length == grid[i].length == 3
#
# 0 <= grid[i][j] <= 9
#
# Sum of grid is equal to 9.
#

# @lc code=start
from itertools import permutations
from typing import List


class Solution:
    def minimumMoves(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        3x3 grid with 9 stones; move stones orthogonally (Manhattan). Make every cell have one.

        Algorithm:
        - Collect empty cells and extra stones (each surplus unit as a source).
        - Try all bijections source->empty; cost = sum of Manhattan distances; take min.

        Complexity: O(m!) with m <= 9 empties, constant grid size.
        """
        empties: List[tuple[int, int]] = []
        extras: List[tuple[int, int]] = []
        for i in range(3):
            for j in range(3):
                if grid[i][j] == 0:
                    empties.append((i, j))
                else:
                    for _ in range(grid[i][j] - 1):
                        extras.append((i, j))
        if not empties:
            return 0
        ans = 10**9
        for perm in permutations(extras):
            cost = 0
            for (x1, y1), (x2, y2) in zip(perm, empties):
                cost += abs(x1 - x2) + abs(y1 - y2)
            ans = min(ans, cost)
        return ans
# @lc code=end
