#
# @lc app=leetcode id=723 lang=python3
#
# [723] Candy Crush
#
# https://leetcode.com/problems/candy-crush/description/
#
# algorithms
# Medium (77.40%)
# Likes:    1072
# Dislikes: 549
# Total Accepted:    91.2K
# Total Submissions: 117.9K
# Testcase Example:  '[[110,5,112,113,114],[210,211,5,213,214],[310,311,3,313,314],[410,411,412,5,414],[5,1,512,3,3],[610,4,1,613,614],[710,1,2,713,714],[810,1,2,1,1],[1,1,2,2,2],[4,1,4,4,1014]]'
#
# This question is about implementing a basic elimination algorithm for Candy
# Crush.
# 
# Given an m x n integer array board representing the grid of candy where
# board[i][j] represents the type of candy. A value of board[i][j] == 0
# represents that the cell is empty.
# 
# The given board represents the state of the game following the player's move.
# Now, you need to restore the board to a stable state by crushing candies
# according to the following rules:
# 
# 
# If three or more candies of the same type are adjacent vertically or
# horizontally, crush them all at the same time - these positions become
# empty.
# After crushing all candies simultaneously, if an empty space on the board has
# candies on top of itself, then these candies will drop until they hit a candy
# or bottom at the same time. No new candies will drop outside the top
# boundary.
# After the above steps, there may exist more candies that can be crushed. If
# so, you need to repeat the above steps.
# If there does not exist more candies that can be crushed (i.e., the board is
# stable), then return the current board.
# 
# 
# You need to perform the above rules until the board becomes stable, then
# return the stable board.
# 
# 
# Example 1:
# 
# 
# Input: board =
# [[110,5,112,113,114],[210,211,5,213,214],[310,311,3,313,314],[410,411,412,5,414],[5,1,512,3,3],[610,4,1,613,614],[710,1,2,713,714],[810,1,2,1,1],[1,1,2,2,2],[4,1,4,4,1014]]
# Output:
# [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[110,0,0,0,114],[210,0,0,0,214],[310,0,0,113,314],[410,0,0,213,414],[610,211,112,313,614],[710,311,412,613,714],[810,411,512,713,1014]]
# 
# 
# Example 2:
# 
# 
# Input: board = [[1,3,5,5,2],[3,4,3,3,1],[3,2,4,5,2],[2,4,4,5,5],[1,4,4,1,1]]
# Output: [[1,3,0,0,0],[3,4,0,5,2],[3,2,0,3,1],[2,4,0,5,2],[1,4,3,1,1]]
# 
# 
# 
# Constraints:
# 
# 
# m == board.length
# n == board[i].length
# 3 <= m, n <= 50
# 1 <= board[i][j] <= 2000
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def candyCrush(self, board: List[List[int]]) -> List[List[int]]:
        m, n = len(board), len(board[0])
        changed = True
        while changed:
            changed = False
            crush = [[False] * n for _ in range(m)]

            for r in range(m):
                c = 0
                while c < n:
                    c2 = c + 1
                    while c2 < n and abs(board[r][c2]) == abs(board[r][c]):
                        c2 += 1
                    if board[r][c] != 0 and c2 - c >= 3:
                        changed = True
                        for x in range(c, c2):
                            crush[r][x] = True
                    c = c2

            for c in range(n):
                r = 0
                while r < m:
                    r2 = r + 1
                    while r2 < m and abs(board[r2][c]) == abs(board[r][c]):
                        r2 += 1
                    if board[r][c] != 0 and r2 - r >= 3:
                        changed = True
                        for x in range(r, r2):
                            crush[x][c] = True
                    r = r2

            if not changed:
                break

            for c in range(n):
                write = m - 1
                for r in range(m - 1, -1, -1):
                    if not crush[r][c]:
                        board[write][c] = board[r][c]
                        write -= 1
                for r in range(write, -1, -1):
                    board[r][c] = 0
        return board
# @lc code=end

"""
Interview explanation:
Repeatedly mark all horizontal and vertical runs of length at least three, crush them simultaneously, then apply gravity column by column. Simultaneous marking is important because a candy can belong to both a horizontal and vertical run.

Data structure: a boolean mark grid records candies to remove before gravity mutates the board.

Edge cases: zeros are ignored and should not form runs. The loop stops only after a full pass finds no crushable run.

Complexity: each pass scans O(mn) cells and applies O(mn) gravity. The number of passes is data-dependent but bounded for the finite board. Space is O(mn) for marks.
"""
