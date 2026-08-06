#
# @lc app=leetcode id=1778 lang=python3
#
# [1778] Shortest Path in a Hidden Grid
#
# https://leetcode.com/problems/shortest-path-in-a-hidden-grid/description/
#
# algorithms
# Medium (44.69%)
# Likes:    209
# Dislikes: 89
# Total Accepted:    17.6K
# Total Submissions: 39.5K
# Testcase Example:  "[[1,2],[-1,0]]"
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
# You want to find the minimum distance to the target cell. However, you
# do not know the grid's dimensions, the starting cell, nor the target
# cell. You are only allowed to ask queries to the GridMaster object.
#
# Thr GridMaster class has the following functions:
#
# boolean canMove(char direction) Returns true if the robot can move in
# that direction. Otherwise, it returns false.
#
# void move(char direction) Moves the robot in that direction. If this
# move would move the robot to a blocked cell or off the grid, the move
# will be ignored, and the robot will remain in the same position.
#
# boolean isTarget() Returns true if the robot is currently on the target
# cell. Otherwise, it returns false.
#
# Note that direction in the above functions should be a character from
# {'U','D','L','R'}, representing the directions up, down, left, and
# right, respectively.
#
# Return the minimum distance between the robot's initial starting cell
# and the target cell. If there is no valid path between the cells, return
# -1.
#
# Custom testing:
#
# The test input is read as a 2D matrix grid of size m x n where:
#
# grid[i][j] == -1 indicates that the robot is in cell (i, j) (the
# starting cell).
#
# grid[i][j] == 0 indicates that the cell (i, j) is blocked.
#
# grid[i][j] == 1 indicates that the cell (i, j) is empty.
#
# grid[i][j] == 2 indicates that the cell (i, j) is the target cell.
#
# There is exactly one -1 and 2 in grid. Remember that you will not have
# this information in your code.
#
# Example 1:
#
# Input: grid = [[1,2],[-1,0]]
# Output: 2
# Explanation: One possible interaction is described below:
# The robot is initially standing on cell (1, 0), denoted by the -1.
# - master.canMove('U') returns true.
# - master.canMove('D') returns false.
# - master.canMove('L') returns false.
# - master.canMove('R') returns false.
# - master.move('U') moves the robot to the cell (0, 0).
# - master.isTarget() returns false.
# - master.canMove('U') returns false.
# - master.canMove('D') returns true.
# - master.canMove('L') returns false.
# - master.canMove('R') returns true.
# - master.move('R') moves the robot to the cell (0, 1).
# - master.isTarget() returns true.
# We now know that the target is the cell (0, 1), and the shortest path to
# the target cell is 2.
#
# Example 2:
#
# Input: grid = [[0,0,-1],[1,1,1],[2,0,0]]
# Output: 4
# Explanation: The minimum distance between the robot and the target cell
# is 4.
#
# Example 3:
#
# Input: grid = [[-1,0],[0,2]]
# Output: -1
# Explanation: There is no path from the robot to the target cell.
#
# Constraints:
#
# 1 <= n, m <= 500
#
# m == grid.length
#
# n == grid[i].length
#
# grid[i][j] is either -1, 0, 1, or 2.
#
# There is exactly one -1 in grid.
#
# There is exactly one 2 in grid.
#
# @lc code=start
from collections import deque


class GridMaster:
    """Judge-provided interactive API for the hidden grid (documented for interviews)."""

    def canMove(self, direction: str) -> bool:
        """
        Interview explanation:
        Public API: return whether a step in direction ('U','D','L','R') from the
        current cell stays in-bounds and is not blocked.

        Algorithm:
        - Provided by the judge / interactive environment.

        Complexity: O(1).
        """
        raise NotImplementedError("Provided by the LeetCode judge")

    def move(self, direction: str) -> bool:
        """
        Interview explanation:
        Public API: move one step in direction if canMove is true; update the
        master's current position. Returns whether the move succeeded.

        Algorithm:
        - Provided by the judge / interactive environment.

        Complexity: O(1).
        """
        raise NotImplementedError("Provided by the LeetCode judge")

    def isTarget(self) -> bool:
        """
        Interview explanation:
        Public API: return True iff the master's current cell is the target.

        Algorithm:
        - Provided by the judge / interactive environment.

        Complexity: O(1).
        """
        raise NotImplementedError("Provided by the LeetCode judge")


class Solution:
    def findShortestPath(self, master: "GridMaster") -> int:
        """
        Interview explanation:
        Premium + GridMaster design: grid is hidden; explore via canMove/move/
        isTarget. DFS/backtracking maps all reachable cells (mark target), then
        BFS on the discovered graph for the shortest path length.

        Algorithm:
        - dirs map U/D/L/R to deltas + reverse moves for backtracking.
        - DFS from (0,0): record cells; if isTarget mark target; try 4 dirs
          with move + recurse + move back.
        - BFS from (0,0) on recorded cells to target; return dist or -1.

        Complexity: O(R*C) explore + BFS.
        """
        dirs = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
        back = {"U": "D", "D": "U", "L": "R", "R": "L"}
        seen = {(0, 0)}
        target = None

        def dfs(r: int, c: int) -> None:
            nonlocal target
            if master.isTarget():
                target = (r, c)
            for d, (dr, dc) in dirs.items():
                nr, nc = r + dr, c + dc
                if (nr, nc) not in seen and master.canMove(d):
                    seen.add((nr, nc))
                    master.move(d)
                    dfs(nr, nc)
                    master.move(back[d])

        dfs(0, 0)
        if target is None:
            return -1
        q = deque([(0, 0, 0)])
        vis = {(0, 0)}
        while q:
            r, c, dist = q.popleft()
            if (r, c) == target:
                return dist
            for dr, dc in dirs.values():
                nr, nc = r + dr, c + dc
                if (nr, nc) in seen and (nr, nc) not in vis:
                    vis.add((nr, nc))
                    q.append((nr, nc, dist + 1))
        return -1
# @lc code=end
