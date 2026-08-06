#
# @lc app=leetcode id=1030 lang=python3
#
# [1030] Matrix Cells in Distance Order
#
# https://leetcode.com/problems/matrix-cells-in-distance-order/description/
#
# algorithms
# Easy (74.5%)
# Likes:    826
# Dislikes: 346
# Total Accepted:    82.0K
# Total Submissions: 110K
# Testcase Example:  "1"
#
# You are given four integers row, cols, rCenter, and cCenter. There is a rows
# x cols matrix and you are on the cell with the coordinates (rCenter,
# cCenter).
#
# Return the coordinates of all cells in the matrix, sorted by their distance
# from (rCenter, cCenter) from the smallest distance to the largest distance.
# You may return the answer in any order that satisfies this condition.
#
# The distance between two cells (r_1, c_1) and (r_2, c_2) is |r_1 - r_2| +
# |c_1 - c_2|.
#
# Example 1:
#
# Input: rows = 1, cols = 2, rCenter = 0, cCenter = 0
# Output: [[0,0],[0,1]]
# Explanation: The distances from (0, 0) to other cells are: [0,1]
#
# Example 2:
#
# Input: rows = 2, cols = 2, rCenter = 0, cCenter = 1
# Output: [[0,1],[0,0],[1,1],[1,0]]
# Explanation: The distances from (0, 1) to other cells are: [0,1,1,2]
# The answer [[0,1],[1,1],[0,0],[1,0]] would also be accepted as correct.
#
# Example 3:
#
# Input: rows = 2, cols = 3, rCenter = 1, cCenter = 2
# Output: [[1,2],[0,2],[1,1],[0,1],[1,0],[0,0]]
# Explanation: The distances from (1, 2) to other cells are: [0,1,1,2,2,3]
# There are other answers that would also be accepted as correct, such as
# [[1,2],[1,1],[0,2],[1,0],[0,1],[0,0]].
#
# Constraints:
#
# 1 <= rows, cols <= 100
#
# 0 <= rCenter < rows
#
# 0 <= cCenter < cols
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def allCellsDistOrder(self, rows: int, cols: int, rCenter: int, cCenter: int) -> List[List[int]]:
        """
        Interview explanation:
        Sort all cells by Manhattan distance to (rCenter, cCenter).

        Algorithm:
        - Generate all (r,c); sort by abs(r-r0)+abs(c-c0)

        Complexity: O(R*C log(R*C)) time, O(R*C) space.
        """
        cells = [[r, c] for r in range(rows) for c in range(cols)]
        cells.sort(key=lambda x: abs(x[0] - rCenter) + abs(x[1] - cCenter))
        return cells

    def allCellsDistOrder_bfs(self, rows: int, cols: int, rCenter: int, cCenter: int) -> List[List[int]]:
        """
        Interview explanation:
        Alternate classic BFS from center: visit cells by increasing Manhattan
        distance (4-directional BFS yields sorted order for Manhattan).

        Algorithm:
        - q=deque([(r0,c0)]); seen; collect order

        Complexity: O(R*C) time and space.
        """
        seen = [[False] * cols for _ in range(rows)]
        q = deque([(rCenter, cCenter)])
        seen[rCenter][cCenter] = True
        ans = []
        while q:
            r, c = q.popleft()
            ans.append([r, c])
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not seen[nr][nc]:
                    seen[nr][nc] = True
                    q.append((nr, nc))
        return ans
# @lc code=end
