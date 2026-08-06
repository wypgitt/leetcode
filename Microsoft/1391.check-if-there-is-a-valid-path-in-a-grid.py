#
# @lc app=leetcode id=1391 lang=python3
#
# [1391] Check if There is a Valid Path in a Grid
#
# https://leetcode.com/problems/check-if-there-is-a-valid-path-in-a-grid/description/
#
# algorithms
# Medium (64.49%)
# Likes:    1081
# Dislikes: 349
# Total Accepted:    109K
# Total Submissions: 169K
# Testcase Example:  "[[3],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2],[2]]"
#
# You are given an m x n grid. Each cell of grid represents a street. The
# street of grid[i][j] can be:
#
# 1 which means a street connecting the left cell and the right cell.
#
# 2 which means a street connecting the upper cell and the lower cell.
#
# 3 which means a street connecting the left cell and the lower cell.
#
# 4 which means a street connecting the right cell and the lower cell.
#
# 5 which means a street connecting the left cell and the upper cell.
#
# 6 which means a street connecting the right cell and the upper cell.
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
# Example 1:
#
# Input: grid = [[2,4,3],[6,5,2]]
# Output: true
# Explanation: As shown you can start at cell (0, 0) and visit all the cells of
# the grid to reach (m - 1, n - 1).
#
# Example 2:
#
# Input: grid = [[1,2,1],[1,2,1]]
# Output: false
# Explanation: As shown you the street at cell (0, 0) is not connected with any
# street of any other cell and you will get stuck at cell (0, 0)
#
# Example 3:
#
# Input: grid = [[1,1,2]]
# Output: false
# Explanation: You will get stuck at cell (0, 1) and you cannot reach cell (0,
# 2).
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 300
#
# 1 <= grid[i][j] <= 6
#

# @lc code=start

from collections import deque
from typing import List


class Solution:
    def hasValidPath(self, grid: List[List[int]]) -> bool:
        """
        Interview explanation:
        Street types 1-6 connect specific sides. BFS/DFS from (0,0) only through
        mutually compatible neighboring streets to reach bottom-right.

        Algorithm:
        - dirs per type; for move to neighbor, require reciprocal connection
        - BFS visited cells

        Complexity: O(mn) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        # L R U D as dx,dy and opposite index
        # connections: set of directions each type opens: 0=L,1=R,2=U,3=D
        conn = {
            1: {0, 1},
            2: {2, 3},
            3: {0, 3},
            4: {1, 3},
            5: {0, 2},
            6: {1, 2},
        }
        delta = {0: (0, -1), 1: (0, 1), 2: (-1, 0), 3: (1, 0)}
        opp = {0: 1, 1: 0, 2: 3, 3: 2}
        q = deque([(0, 0)])
        vis = {(0, 0)}
        while q:
            r, c = q.popleft()
            if r == m - 1 and c == n - 1:
                return True
            for d in conn[grid[r][c]]:
                dr, dc = delta[d]
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and (nr, nc) not in vis:
                    if opp[d] in conn[grid[nr][nc]]:
                        vis.add((nr, nc))
                        q.append((nr, nc))
        return False
# @lc code=end
