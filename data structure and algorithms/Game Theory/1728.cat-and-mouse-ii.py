#
# @lc app=leetcode id=1728 lang=python3
#
# [1728] Cat and Mouse II
#
# https://leetcode.com/problems/cat-and-mouse-ii/description/
#
# algorithms
# Hard (40.21%)
# Likes:    292
# Dislikes: 49
# Total Accepted:    10.0K
# Total Submissions: 24.8K
# Testcase Example:  "[\"####F\",\"#C...\",\"M....\"]"
#
# A game is played by a cat and a mouse named Cat and Mouse.
#
# The environment is represented by a grid of size rows x cols, where each
# element is a wall, floor, player (Cat, Mouse), or food.
#
# Players are represented by the characters 'C'(Cat),'M'(Mouse).
#
# Floors are represented by the character '.' and can be walked on.
#
# Walls are represented by the character '#' and cannot be walked on.
#
# Food is represented by the character 'F' and can be walked on.
#
# There is only one of each character 'C', 'M', and 'F' in grid.
#
# Mouse and Cat play according to the following rules:
#
# Mouse moves first, then they take turns to move.
#
# During each turn, Cat and Mouse can jump in one of the four directions (left,
# right, up, down). They cannot jump over the wall nor outside of the grid.
#
# catJump, mouseJump are the maximum lengths Cat and Mouse can jump at a time,
# respectively. Cat and Mouse can jump less than the maximum length.
#
# Staying in the same position is allowed.
#
# Mouse can jump over Cat.
#
# The game can end in 4 ways:
#
# If Cat occupies the same position as Mouse, Cat wins.
#
# If Cat reaches the food first, Cat wins.
#
# If Mouse reaches the food first, Mouse wins.
#
# If Mouse cannot get to the food within 1000 turns, Cat wins.
#
# Given a rows x cols matrix grid and two integers catJump and mouseJump,
# return true if Mouse can win the game if both Cat and Mouse play optimally,
# otherwise return false.
#
# Example 1:
#
# Input: grid = ["####F","#C...","M...."], catJump = 1, mouseJump = 2
# Output: true
# Explanation: Cat cannot catch Mouse on its turn nor can it get the food
# before Mouse.
#
# Example 2:
#
# Input: grid = ["M.C...F"], catJump = 1, mouseJump = 4
# Output: true
#
# Example 3:
#
# Input: grid = ["M.C...F"], catJump = 1, mouseJump = 3
# Output: false
#
# Constraints:
#
# rows == grid.length
#
# cols = grid[i].length
#
# 1 <= rows, cols <= 8
#
# grid[i][j] consist only of characters 'C', 'M', 'F', '.', and '#'.
#
# There is only one of each character 'C', 'M', and 'F' in grid.
#
# 1 <= catJump, mouseJump <= 8
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def canMouseWin(self, grid: List[str], catJump: int, mouseJump: int) -> bool:
        """
        Interview explanation:
        Cat and Mouse II on a grid. Mouse moves first; each jumps up to its jump
        length in 4 dirs or stays. Mouse wins by food first; cat wins by catching
        mouse, reaching food, or draw after enough turns. Memoized minimax.

        Algorithm:
        - Locate M, C, F; walls set.
        - dfs(mr,mc,cr,cc,turn) with jump generator; mouse even turns.
        - Cap turns at ~2*R*C to declare draw (cat win).

        Complexity: O((RC)^2 * turns * jumps) states; RC <= 64.
        """
        rows, cols = len(grid), len(grid[0])
        wall = set()
        food = mouse = cat = None
        for i in range(rows):
            for j in range(cols):
                ch = grid[i][j]
                if ch == '#':
                    wall.add((i, j))
                elif ch == 'F':
                    food = (i, j)
                elif ch == 'M':
                    mouse = (i, j)
                elif ch == 'C':
                    cat = (i, j)

        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        max_turns = rows * cols * 2

        def jumps(pos, jump):
            r, c = pos
            yield pos
            for dr, dc in dirs:
                for step in range(1, jump + 1):
                    nr, nc = r + dr * step, c + dc * step
                    if not (0 <= nr < rows and 0 <= nc < cols) or (nr, nc) in wall:
                        break
                    yield (nr, nc)

        @lru_cache(None)
        def dfs(mr, mc, cr, cc, turn):
            if turn > max_turns:
                return False
            if (mr, mc) == (cr, cc) or (cr, cc) == food:
                return False
            if (mr, mc) == food:
                return True
            if turn % 2 == 0:
                for nr, nc in jumps((mr, mc), mouseJump):
                    if dfs(nr, nc, cr, cc, turn + 1):
                        return True
                return False
            for nr, nc in jumps((cr, cc), catJump):
                if not dfs(mr, mc, nr, nc, turn + 1):
                    return False
            return True

        return dfs(mouse[0], mouse[1], cat[0], cat[1], 0)
# @lc code=end
