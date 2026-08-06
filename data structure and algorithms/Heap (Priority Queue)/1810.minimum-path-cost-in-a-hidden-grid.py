#
# @lc app=leetcode id=1810 lang=python3
#
# [1810] Minimum Path Cost in a Hidden Grid
#
# https://leetcode.com/problems/minimum-path-cost-in-a-hidden-grid/description/
#
# algorithms
# Medium (59.12%)
# Likes:    95
# Dislikes: 33
# Total Accepted:    5.7K
# Total Submissions: 9.7K
# Testcase Example:  "[[2,3],[1,1]]\n0\n1\n1\n0"
#
#
# This is an interactive problem.
#
# There is a robot in a hidden grid, and you are trying to get it from its
# starting cell to the target cell in this grid. The grid is of size m x
# n, and each cell in the grid is either empty or blocked. It is
# guaranteed that the starting cell and the target cell are different, and
# neither of them is blocked.
#
# Each cell has a cost that you need to pay each time you move to the
# cell. The starting cell's cost is not applied before the robot moves.
#
# You want to find the minimum total cost to move the robot to the target
# cell. However, you do not know the grid's dimensions, the starting cell,
# nor the target cell. You are only allowed to ask queries to the
# GridMaster object.
#
# The GridMaster class has the following functions:
#
# boolean canMove(char direction) Returns true if the robot can move in
# that direction. Otherwise, it returns false.
#
# int move(char direction) Moves the robot in that direction and returns
# the cost of moving to that cell. If this move would move the robot to a
# blocked cell or off the grid, the move will be ignored, the robot will
# remain in the same position, and the function will return -1.
#
# boolean isTarget() Returns true if the robot is currently on the target
# cell. Otherwise, it returns false.
#
# Note that direction in the above functions should be a character from
# {'U','D','L','R'}, representing the directions up, down, left, and
# right, respectively.
#
# Return the minimum total cost to get the robot from its initial starting
# cell to the target cell. If there is no valid path between the cells,
# return -1.
#
# Custom testing:
#
# The test input is read as a 2D matrix grid of size m x n and four
# integers r1, c1, r2, and c2 where:
#
# grid[i][j] == 0 indicates that the cell (i, j) is blocked.
#
# grid[i][j] >= 1 indicates that the cell (i, j) is empty and grid[i][j]
# is the cost to move to that cell.
#
# (r1, c1) is the starting cell of the robot.
#
# (r2, c2) is the target cell of the robot.
#
# Remember that you will not have this information in your code.
#
# Example 1:
#
# Input: grid = [[2,3],[1,1]], r1 = 0, c1 = 1, r2 = 1, c2 = 0
# Output: 2
# Explanation: One possible interaction is described below:
# The robot is initially standing on cell (0, 1), denoted by the 3.
# - master.canMove('U') returns false.
# - master.canMove('D') returns true.
# - master.canMove('L') returns true.
# - master.canMove('R') returns false.
# - master.move('L') moves the robot to the cell (0, 0) and returns 2.
# - master.isTarget() returns false.
# - master.canMove('U') returns false.
# - master.canMove('D') returns true.
# - master.canMove('L') returns false.
# - master.canMove('R') returns true.
# - master.move('D') moves the robot to the cell (1, 0) and returns 1.
# - master.isTarget() returns true.
# - master.move('L') doesn't move the robot and returns -1.
# - master.move('R') moves the robot to the cell (1, 1) and returns 1.
# We now know that the target is the cell (1, 0), and the minimum total
# cost to reach it is 2.
#
# Example 2:
#
# Input: grid = [[0,3,1],[3,4,2],[1,2,0]], r1 = 2, c1 = 0, r2 = 0, c2 = 2
# Output: 9
# Explanation: The minimum cost path is (2,0) -> (2,1) -> (1,1) -> (1,2)
# -> (0,2).
#
# Example 3:
#
# Input: grid = [[1,0],[0,1]], r1 = 0, c1 = 0, r2 = 1, c2 = 1
# Output: -1
# Explanation: There is no path from the robot to the target cell.
#
# Constraints:
#
# 1 <= n, m <= 100
#
# m == grid.length
#
# n == grid[i].length
#
# 0 <= grid[i][j] <= 100
#
# @lc code=start
from typing import Optional
import heapq


class GridMaster:
    """Judge-provided interactive API for the hidden grid (documented for interviews)."""

    def canMove(self, direction: str) -> bool:
        """
        Interview explanation:
        Public API: whether a step in direction ('U','D','L','R') is allowed
        from the current cell (in-bounds and not blocked).

        Algorithm:
        - Provided by the judge / interactive environment.

        Complexity: O(1).
        """
        raise NotImplementedError("Provided by the LeetCode judge")

    def move(self, direction: str) -> int:
        """
        Interview explanation:
        Public API: move one step if allowed; return the cost of the destination
        cell (grid value). Updates master's position.

        Algorithm:
        - Provided by the judge / interactive environment.

        Complexity: O(1).
        """
        raise NotImplementedError("Provided by the LeetCode judge")

    def isTarget(self) -> bool:
        """
        Interview explanation:
        Public API: True iff current cell is the target.

        Algorithm:
        - Provided by the judge / interactive environment.

        Complexity: O(1).
        """
        raise NotImplementedError("Provided by the LeetCode judge")


class Solution:
    def findShortestPath(self, master: "GridMaster") -> int:
        """
        Interview explanation:
        Premium + GridMaster: explore hidden grid via canMove/move/isTarget,
        record cell costs, then Dijkstra for minimum path cost to target
        (cost = sum of entered cells; start cost may be 0 depending on statement —
        standard: sum of costs of all cells on path except possibly start;
        LeetCode 1810: cost is sum of values of cells visited including target,
        start cell value is given by first move returns; typically map costs then
        Dijkstra where edge into cell adds cell cost).

        Algorithm (DFS map + Dijkstra):
        - DFS/backtrack with move/reverse; store cost[r][c]; mark target.
        - Dijkstra from (0,0): dist to neighbor = dist + cost[nr][nc].
        - Return min dist to target or -1. Start contributes 0 to path sum
          (common convention for this problem: only costs of moved-into cells).

        Complexity: O(RC log(RC)) after O(RC) explore.
        """
        dirs = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
        back = {"U": "D", "D": "U", "L": "R", "R": "L"}
        cost = {(0, 0): 0}
        target = None

        def dfs(r: int, c: int) -> None:
            nonlocal target
            if master.isTarget():
                target = (r, c)
            for d, (dr, dc) in dirs.items():
                nr, nc = r + dr, c + dc
                if (nr, nc) not in cost and master.canMove(d):
                    cell = master.move(d)
                    cost[(nr, nc)] = cell
                    dfs(nr, nc)
                    master.move(back[d])

        dfs(0, 0)
        if target is None:
            return -1

        dist = { (0, 0): 0 }
        pq = [(0, 0, 0)]
        while pq:
            d, r, c = heapq.heappop(pq)
            if (r, c) == target:
                return d
            if d > dist.get((r, c), 10**18):
                continue
            for dr, dc in dirs.values():
                nr, nc = r + dr, c + dc
                if (nr, nc) in cost:
                    nd = d + cost[(nr, nc)]
                    if nd < dist.get((nr, nc), 10**18):
                        dist[(nr, nc)] = nd
                        heapq.heappush(pq, (nd, nr, nc))
        return -1
# @lc code=end
