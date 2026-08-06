#
# @lc app=leetcode id=1706 lang=python3
#
# [1706] Where Will the Ball Fall
#
# https://leetcode.com/problems/where-will-the-ball-fall/description/
#
# algorithms
# Medium (72.34%)
# Likes:    3186
# Dislikes: 182
# Total Accepted:    151K
# Total Submissions: 209K
# Testcase Example:  "[[1,1,1,-1,-1],[1,1,1,-1,-1],[-1,-1,-1,1,1],[1,1,1,1,-1],[-1,-1,-1,-1,-1]]"
#
# You have a 2-D grid of size m x n representing a box, and you have n balls.
# The box is open on the top and bottom sides.
#
# Each cell in the box has a diagonal board spanning two corners of the cell
# that can redirect a ball to the right or to the left.
#
# A board that redirects the ball to the right spans the top-left corner to the
# bottom-right corner and is represented in the grid as 1.
#
# A board that redirects the ball to the left spans the top-right corner to the
# bottom-left corner and is represented in the grid as -1.
#
# We drop one ball at the top of each column of the box. Each ball can get
# stuck in the box or fall out of the bottom. A ball gets stuck if it hits a
# "V" shaped pattern between two boards or if a board redirects the ball into
# either wall of the box.
#
# Return an array answer of size n where answer[i] is the column that the ball
# falls out of at the bottom after dropping the ball from the i^th column at
# the top, or -1 if the ball gets stuck in the box.
#
# Example 1:
#
# Input: grid =
# [[1,1,1,-1,-1],[1,1,1,-1,-1],[-1,-1,-1,1,1],[1,1,1,1,-1],[-1,-1,-1,-1,-1]]
# Output: [1,-1,-1,-1,-1]
# Explanation: This example is shown in the photo.
# Ball b0 is dropped at column 0 and falls out of the box at column 1.
# Ball b1 is dropped at column 1 and will get stuck in the box between column 2
# and 3 and row 1.
# Ball b2 is dropped at column 2 and will get stuck on the box between column 2
# and 3 and row 0.
# Ball b3 is dropped at column 3 and will get stuck on the box between column 2
# and 3 and row 0.
# Ball b4 is dropped at column 4 and will get stuck on the box between column 2
# and 3 and row 1.
#
# Example 2:
#
# Input: grid = [[-1]]
# Output: [-1]
# Explanation: The ball gets stuck against the left wall.
#
# Example 3:
#
# Input: grid =
# [[1,1,1,1,1,1],[-1,-1,-1,-1,-1,-1],[1,1,1,1,1,1],[-1,-1,-1,-1,-1,-1]]
# Output: [0,1,2,3,4,-1]
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 100
#
# grid[i][j] is 1 or -1.
#

# @lc code=start
from typing import List


class Solution:
    def findBall(self, grid: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Balls fall from each top column. At cell with 1 (down-right) go right if neighbor also 1;
        with -1 (down-left) go left if neighbor also -1; else stuck (V shape).

        Algorithm:
        - For each start column, simulate row by row updating column; return -1 if wall/V.

        Complexity: O(m*n) time, O(1) extra space (O(n) for answer).
        """
        m, n = len(grid), len(grid[0])
        ans = []
        for start in range(n):
            c = start
            for r in range(m):
                dir_ = grid[r][c]
                nc = c + dir_
                if nc < 0 or nc >= n or grid[r][nc] != dir_:
                    c = -1
                    break
                c = nc
            ans.append(c)
        return ans

    def findBall_dfs(self, grid: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Alternate: recursive DFS from (0, c) following the same V-check rules.

        Algorithm:
        - dfs(r,c): if r==m return c; else try neighbor consistency.

        Complexity: O(m*n) time, O(m) recursion space.
        """
        m, n = len(grid), len(grid[0])

        def dfs(r: int, c: int) -> int:
            if r == m:
                return c
            dir_ = grid[r][c]
            nc = c + dir_
            if nc < 0 or nc >= n or grid[r][nc] != dir_:
                return -1
            return dfs(r + 1, nc)

        return [dfs(0, c) for c in range(n)]
# @lc code=end
