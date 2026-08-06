#
# @lc app=leetcode id=1970 lang=python3
#
# [1970] Last Day Where You Can Still Cross
#
# https://leetcode.com/problems/last-day-where-you-can-still-cross/description/
#
# algorithms
# Hard (68.74%)
# Likes:    2407
# Dislikes: 48
# Total Accepted:    134K
# Total Submissions: 195K
# Testcase Example:  "2"
#
# There is a 1-based binary matrix where 0 represents land and 1 represents
# water. You are given integers row and col representing the number of rows and
# columns in the matrix, respectively.
#
# Initially on day 0, the entire matrix is land. However, each day a new cell
# becomes flooded with water. You are given a 1-based 2D array cells, where
# cells[i] = [r_i, c_i] represents that on the i^th day, the cell on the r_i^th
# row and c_i^th column (1-based coordinates) will be covered with water (i.e.,
# changed to 1).
#
# You want to find the last day that it is possible to walk from the top to the
# bottom by only walking on land cells. You can start from any cell in the top
# row and end at any cell in the bottom row. You can only travel in the four
# cardinal directions (left, right, up, and down).
#
# Return the last day where it is possible to walk from the top to the bottom
# by only walking on land cells.
#
# Example 1:
#
# Input: row = 2, col = 2, cells = [[1,1],[2,1],[1,2],[2,2]]
# Output: 2
# Explanation: The above image depicts how the matrix changes each day starting
# from day 0.
# The last day where it is possible to cross from top to bottom is on day 2.
#
# Example 2:
#
# Input: row = 2, col = 2, cells = [[1,1],[1,2],[2,1],[2,2]]
# Output: 1
# Explanation: The above image depicts how the matrix changes each day starting
# from day 0.
# The last day where it is possible to cross from top to bottom is on day 1.
#
# Example 3:
#
# Input: row = 3, col = 3, cells =
# [[1,2],[2,1],[3,3],[2,2],[1,1],[1,3],[2,3],[3,2],[3,1]]
# Output: 3
# Explanation: The above image depicts how the matrix changes each day starting
# from day 0.
# The last day where it is possible to cross from top to bottom is on day 3.
#
# Constraints:
#
# 2 <= row, col <= 2 * 10^4
#
# 4 <= row * col <= 2 * 10^4
#
# cells.length == row * col
#
# 1 <= r_i <= row
#
# 1 <= c_i <= col
#
# All the values of cells are unique.
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def latestDayToCross(self, row: int, col: int, cells: List[List[int]]) -> int:
        """
        Interview explanation:
        Cells flood day-by-day. Latest day you can still walk top→bottom on land.
        Binary search day d; BFS/DFS on grid with first d cells flooded.

        Algorithm:
        - lo,hi = 1,len(cells); check(mid): mark cells[:mid] water; BFS from top.

        Complexity: O(row*col * log(row*col)) time, O(row*col) space.
        """
        def ok(day: int) -> bool:
            water = set((r - 1, c - 1) for r, c in cells[:day])
            q = deque()
            seen = [[False] * col for _ in range(row)]
            for c in range(col):
                if (0, c) not in water:
                    q.append((0, c))
                    seen[0][c] = True
            while q:
                r, c = q.popleft()
                if r == row - 1:
                    return True
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                    if 0 <= nr < row and 0 <= nc < col and not seen[nr][nc] and (nr, nc) not in water:
                        seen[nr][nc] = True
                        q.append((nr, nc))
            return False

        lo, hi = 1, len(cells)
        ans = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if ok(mid):
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans

    def latestDayToCross_uf(self, row: int, col: int, cells: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic alternate: process days reverse (water→land). Union land cells;
        connect to virtual top/bottom nodes; first day top meets bottom.

        Algorithm:
        - Start full water; add land from last day backward; UF neighbors + top/bottom.

        Complexity: O(row*col * α) time, O(row*col) space.
        """
        parent = list(range(row * col + 2))
        TOP, BOT = row * col, row * col + 1

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        land = [[False] * col for _ in range(row)]
        for day in range(len(cells) - 1, -1, -1):
            r, c = cells[day][0] - 1, cells[day][1] - 1
            land[r][c] = True
            idx = r * col + c
            if r == 0:
                union(idx, TOP)
            if r == row - 1:
                union(idx, BOT)
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < row and 0 <= nc < col and land[nr][nc]:
                    union(idx, nr * col + nc)
            if find(TOP) == find(BOT):
                return day
        return 0
# @lc code=end

