#
# @lc app=leetcode id=2852 lang=python3
#
# [2852] Sum of Remoteness of All Cells
#
# https://leetcode.com/problems/sum-of-remoteness-of-all-cells/description/
#
# algorithms
# Medium (70.78%)
# Likes:    59
# Dislikes: 16
# Total Accepted:    6.6K
# Total Submissions: 9.4K
# Testcase Example:  "[[-1,1,-1],[5,-1,4],[-1,3,-1]]"
#
#
# You are given a 0-indexed matrix grid of order n * n. Each cell in this
# matrix has a value grid[i][j], which is either a positive integer or -1
# representing a blocked cell.
#
# You can move from a non-blocked cell to any non-blocked cell that shares
# an edge.
#
# For any cell (i, j), we represent its remoteness as R[i][j] which is
# defined as the following:
#
# If the cell (i, j) is a non-blocked cell, R[i][j] is the sum of the
# values grid[x][y] such that there is no path from the non-blocked cell
# (x, y) to the cell (i, j).
#
# For blocked cells, R[i][j] == 0.
#
# Return the sum of R[i][j] over all cells.
#
# Example 1:
#
# Input: grid = [[-1,1,-1],[5,-1,4],[-1,3,-1]]
# Output: 39
# Explanation: In the picture above, there are four grids. The top-left
# grid contains the initial values in the grid. Blocked cells are colored
# black, and other cells get their values as it is in the input. In the
# top-right grid, you can see the value of R[i][j] for all cells. So the
# answer would be the sum of them. That is: 0 + 12 + 0 + 8 + 0 + 9 + 0 +
# 10 + 0 = 39.
# Let's jump on the bottom-left grid in the above picture and calculate
# R[0][1] (the target cell is colored green). We should sum up the value
# of cells that can't be reached by the cell (0, 1). These cells are
# colored yellow in this grid. So R[0][1] = 5 + 4 + 3 = 12.
# Now let's jump on the bottom-right grid in the above picture and
# calculate R[1][2] (the target cell is colored green). We should sum up
# the value of cells that can't be reached by the cell (1, 2). These cells
# are colored yellow in this grid. So R[1][2] = 1 + 5 + 3 = 9.
#
# Example 2:
#
# Input: grid = [[-1,3,4],[-1,-1,-1],[3,-1,-1]]
# Output: 13
# Explanation: In the picture above, there are four grids. The top-left
# grid contains the initial values in the grid. Blocked cells are colored
# black, and other cells get their values as it is in the input. In the
# top-right grid, you can see the value of R[i][j] for all cells. So the
# answer would be the sum of them. That is: 3 + 3 + 0 + 0 + 0 + 0 + 7 + 0
# + 0 = 13.
# Let's jump on the bottom-left grid in the above picture and calculate
# R[0][2] (the target cell is colored green). We should sum up the value
# of cells that can't be reached by the cell (0, 2). This cell is colored
# yellow in this grid. So R[0][2] = 3.
# Now let's jump on the bottom-right grid in the above picture and
# calculate R[2][0] (the target cell is colored green). We should sum up
# the value of cells that can't be reached by the cell (2, 0). These cells
# are colored yellow in this grid. So R[2][0] = 3 + 4 = 7.
#
# Example 3:
#
# Input: grid = [[1]]
# Output: 0
# Explanation: Since there are no other cells than (0, 0), R[0][0] is
# equal to 0. So the sum of R[i][j] over all cells would be 0.
#
# Constraints:
#
# 1 <= n <= 300
#
# 1 <= grid[i][j] <= 10^6 or grid[i][j] == -1
#
# @lc code=start
from typing import List


class Solution:
    def sumRemoteness(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium: n x n grid; -1 blocked, else positive. Remoteness of a cell = sum of
        values of non-blocked cells unreachable via 4-direction moves. Sum all remoteness.

        Algorithm:
        - Total sum S of non-blocked cells.
        - BFS/DFS each component: size t, sum s; each cell contributes S - s.
        - Answer += t * (S - s) per component.

        Complexity: O(n^2) time and space.
        """
        n = len(grid)
        total = sum(v for row in grid for v in row if v != -1)
        ans = 0
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for i in range(n):
            for j in range(n):
                if grid[i][j] != -1:
                    stack = [(i, j)]
                    comp_sum = grid[i][j]
                    count = 1
                    grid[i][j] = -1
                    while stack:
                        x, y = stack.pop()
                        for dx, dy in dirs:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] != -1:
                                comp_sum += grid[nx][ny]
                                count += 1
                                grid[nx][ny] = -1
                                stack.append((nx, ny))
                    ans += count * (total - comp_sum)
        return ans

    def sumRemoteness_dfs(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate recursive DFS component aggregation (same formula).

        Algorithm:
        - Recurse 4-neighbors; mark visited as -1; accumulate (sum, count).

        Complexity: O(n^2) time and space.
        """
        n = len(grid)
        total = sum(v for row in grid for v in row if v != -1)
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

        def dfs(i: int, j: int) -> tuple[int, int]:
            s, t = grid[i][j], 1
            grid[i][j] = -1
            for dx, dy in dirs:
                x, y = i + dx, j + dy
                if 0 <= x < n and 0 <= y < n and grid[x][y] != -1:
                    s1, t1 = dfs(x, y)
                    s += s1
                    t += t1
            return s, t

        ans = 0
        for i in range(n):
            for j in range(n):
                if grid[i][j] != -1:
                    s, t = dfs(i, j)
                    ans += t * (total - s)
        return ans
# @lc code=end
