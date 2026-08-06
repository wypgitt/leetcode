#
# @lc app=leetcode id=1210 lang=python3
#
# [1210] Minimum Moves to Reach Target with Rotations
#
# https://leetcode.com/problems/minimum-moves-to-reach-target-with-rotations/description/
#
# algorithms
# Hard (52.6%)
# Likes:    291
# Dislikes: 76
# Total Accepted:    13.3K
# Total Submissions: 25.2K
# Testcase Example:  "[[0,0,0,0,0,1],[1,1,0,0,1,0],[0,0,0,0,1,1],[0,0,1,0,1,0],[0,1,1,0,0,0],[0,1,1,0,0,0]]\r"
#
# In an n*n grid, there is a snake that spans 2 cells and starts moving from
# the top left corner at (0, 0) and (0, 1). The grid has empty cells
# represented by zeros and blocked cells represented by ones. The snake wants
# to reach the lower right corner at (n-1, n-2) and (n-1, n-1).
#
# In one move the snake can:
#
# Move one cell to the right if there are no blocked cells there. This move
# keeps the horizontal/vertical position of the snake as it is.
#
# Move down one cell if there are no blocked cells there. This move keeps the
# horizontal/vertical position of the snake as it is.
#
# Rotate clockwise if it's in a horizontal position and the two cells under it
# are both empty. In that case the snake moves from (r, c) and (r, c+1) to (r,
# c) and (r+1, c).
#
# Rotate counterclockwise if it's in a vertical position and the two cells to
# its right are both empty. In that case the snake moves from (r, c) and (r+1,
# c) to (r, c) and (r, c+1).
#
# Return the minimum number of moves to reach the target.
#
# If there is no way to reach the target, return -1.
#
# Example 1:
#
# Input: grid = [[0,0,0,0,0,1],
# [1,1,0,0,1,0],
# [0,0,0,0,1,1],
# [0,0,1,0,1,0],
# [0,1,1,0,0,0],
# [0,1,1,0,0,0]]
# Output: 11
# Explanation:
# One possible solution is [right, right, rotate clockwise, right, down, down,
# down, down, rotate counterclockwise, right, down].
#
# Example 2:
#
# Input: grid = [[0,0,1,1,1,1],
# [0,0,0,0,1,1],
# [1,1,0,0,0,1],
# [1,1,1,0,0,1],
# [1,1,1,0,0,1],
# [1,1,1,0,0,0]]
# Output: 9
#
# Constraints:
#
# 2 <= n <= 100
#
# 0 <= grid[i][j] <= 1
#
# It is guaranteed that the snake starts at empty cells.
#


# @lc code=start
from typing import List
from collections import deque

class Solution:
    def minimumMoves(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Snake of length 2 on grid; states are (tail_r, tail_c, orientation)
        where ori=0 horizontal, 1 vertical. BFS shortest path to tail at
        (n-1,n-2) horizontal. Moves: crawl forward or clockwise/counterclockwise
        rotate when 2x2 clear.

        Algorithm:
        - BFS queue of (r,c,ori,steps); visited set
        - Horizontal: right if empty; down if both cells below empty; rotate CW
        - Vertical: down if empty; right if both cells right empty; rotate CCW

        Complexity: O(n^2) states/time.
        """
        n = len(grid)
        start = (0, 0, 0)  # r, c, ori
        goal = (n - 1, n - 2, 0)
        q = deque([(0, 0, 0, 0)])
        seen = {(0, 0, 0)}

        def inside(r: int, c: int) -> bool:
            return 0 <= r < n and 0 <= c < n and grid[r][c] == 0

        while q:
            r, c, ori, steps = q.popleft()
            if (r, c, ori) == goal:
                return steps
            if ori == 0:  # horizontal: occupies (r,c) and (r,c+1)
                # crawl right
                if inside(r, c + 2) and (r, c + 1, 0) not in seen:
                    seen.add((r, c + 1, 0))
                    q.append((r, c + 1, 0, steps + 1))
                # crawl down
                if inside(r + 1, c) and inside(r + 1, c + 1) and (r + 1, c, 0) not in seen:
                    seen.add((r + 1, c, 0))
                    q.append((r + 1, c, 0, steps + 1))
                # rotate clockwise
                if inside(r + 1, c) and inside(r + 1, c + 1) and (r, c, 1) not in seen:
                    seen.add((r, c, 1))
                    q.append((r, c, 1, steps + 1))
            else:  # vertical: (r,c) and (r+1,c)
                if inside(r + 2, c) and (r + 1, c, 1) not in seen:
                    seen.add((r + 1, c, 1))
                    q.append((r + 1, c, 1, steps + 1))
                if inside(r, c + 1) and inside(r + 1, c + 1) and (r, c + 1, 1) not in seen:
                    seen.add((r, c + 1, 1))
                    q.append((r, c + 1, 1, steps + 1))
                if inside(r, c + 1) and inside(r + 1, c + 1) and (r, c, 0) not in seen:
                    seen.add((r, c, 0))
                    q.append((r, c, 0, steps + 1))
        return -1
# @lc code=end
