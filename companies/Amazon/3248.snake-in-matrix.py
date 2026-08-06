#
# @lc app=leetcode id=3248 lang=python3
#
# [3248] Snake in Matrix
#
# https://leetcode.com/problems/snake-in-matrix/description/
#
# algorithms
# Easy (82.45%)
# Likes:    183
# Dislikes: 5
# Total Accepted:    79.5K
# Total Submissions: 96.4K
# Testcase Example:  "2\n[\"RIGHT\",\"DOWN\"]"
#
#
# There is a snake in an n x n matrix grid and can move in four possible
# directions. Each cell in the grid is identified by the position:
# grid[i][j] = (i * n) + j.
#
# The snake starts at cell 0 and follows a sequence of commands.
#
# You are given an integer n representing the size of the grid and an
# array of strings commands where each command[i] is either "UP", "RIGHT",
# "DOWN", and "LEFT". It's guaranteed that the snake will remain within
# the grid boundaries throughout its movement.
#
# Return the position of the final cell where the snake ends up after
# executing commands.
#
# Example 1:
#
# Input: n = 2, commands = ["RIGHT","DOWN"]
#
# Output: 3
#
# Explanation:
#
#                         0
#                         1
#
#                         2
#                         3
#
#                         0
#                         1
#
#                         2
#                         3
#
#                         0
#                         1
#
#                         2
#                         3
#
# Example 2:
#
# Input: n = 3, commands = ["DOWN","RIGHT","UP"]
#
# Output: 1
#
# Explanation:
#
#                         0
#                         1
#                         2
#
#                         3
#                         4
#                         5
#
#                         6
#                         7
#                         8
#
#                         0
#                         1
#                         2
#
#                         3
#                         4
#                         5
#
#                         6
#                         7
#                         8
#
#                         0
#                         1
#                         2
#
#                         3
#                         4
#                         5
#
#                         6
#                         7
#                         8
#
#                         0
#                         1
#                         2
#
#                         3
#                         4
#                         5
#
#                         6
#                         7
#                         8
#
# Constraints:
#
# 2 <= n <= 10
#
# 1 <= commands.length <= 100
#
# commands consists only of "UP", "RIGHT", "DOWN", and "LEFT".
#
# The input is generated such the snake will not move outside of the
# boundaries.
#

# @lc code=start
from typing import List


class Solution:
    def finalPositionOfSnake(self, n: int, commands: List[str]) -> int:
        """
        Interview explanation:
        Grid cell (r, c) encodes as r*n + c. Start at 0 and apply moves; stay
        in bounds by guarantee.

        Algorithm:
        - Track (r, c); map UP/DOWN/LEFT/RIGHT to delta; return r*n + c.

        Complexity: O(|commands|) time, O(1) space.
        """
        r = c = 0
        for cmd in commands:
            if cmd == "UP":
                r -= 1
            elif cmd == "DOWN":
                r += 1
            elif cmd == "LEFT":
                c -= 1
            else:
                c += 1
        return r * n + c
# @lc code=end
