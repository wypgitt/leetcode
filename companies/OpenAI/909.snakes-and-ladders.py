#
# @lc app=leetcode id=909 lang=python3
#
# [909] Snakes and Ladders
#
# https://leetcode.com/problems/snakes-and-ladders/description/
#
# algorithms
# Medium (48.22%)
# Likes:    3697
# Dislikes: 1357
# Total Accepted:    377K
# Total Submissions: 781K
# Testcase Example:  "[[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,35,-1,-1,13,-1],[-1,-1,-1,-1,-1,-1],[-1,15,-1,-1,-1,-1]]"
#
# You are given an n x n integer matrix board where the cells are labeled from
# 1 to n^2 in a Boustrophedon style starting from the bottom left of the board
# (i.e. board[n - 1][0]) and alternating direction each row.
#
# You start on square 1 of the board. In each move, starting from square curr,
# do the following:
#
# Choose a destination square next with a label in the range [curr + 1,
# min(curr + 6, n^2)].
#
# This choice simulates the result of a standard 6-sided die roll: i.e., there
# are always at most 6 destinations, regardless of the size of the board.
#
# If next has a snake or ladder, you must move to the destination of that snake
# or ladder. Otherwise, you move to next.
#
# The game ends when you reach the square n^2.
#
# A board square on row r and column c has a snake or ladder if board[r][c] !=
# -1. The destination of that snake or ladder is board[r][c]. Squares 1 and n^2
# are not the starting points of any snake or ladder.
#
# Note that you only take a snake or ladder at most once per dice roll. If the
# destination to a snake or ladder is the start of another snake or ladder, you
# do not follow the subsequent snake or ladder.
#
# For example, suppose the board is [[-1,4],[-1,3]], and on the first move,
# your destination square is 2. You follow the ladder to square 3, but do not
# follow the subsequent ladder to 4.
#
# Return the least number of dice rolls required to reach the square n^2. If it
# is not possible to reach the square, return -1.
#
# Example 1:
#
# Input: board =
# [[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,35,-1,-1,13,-1],[-1,-1,-1,-1,-1,-1],[-1,15,-1,-1,-1,-1]]
# Output: 4
# Explanation:
# In the beginning, you start at square 1 (at row 5, column 0).
# You decide to move to square 2 and must take the ladder to square 15.
# You then decide to move to square 17 and must take the snake to square 13.
# You then decide to move to square 14 and must take the ladder to square 35.
# You then decide to move to square 36, ending the game.
# This is the lowest possible number of moves to reach the last square, so
# return 4.
#
# Example 2:
#
# Input: board = [[-1,-1],[-1,3]]
# Output: 1
#
# Constraints:
#
# n == board.length == board[i].length
#
# 2 <= n <= 20
#
# board[i][j] is either -1 or in the range [1, n^2].
#
# The squares labeled 1 and n^2 are not the starting points of any snake or
# ladder.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def snakesAndLadders(self, board: List[List[int]]) -> int:
        """
        Interview explanation:
        Boustrophedon board labeling. Shortest path with dice 1..6 = BFS on
        cells 1..n^2; teleport via snake/ladder when landing.

        Algorithm (BFS):
        - Map label → (r,c). BFS from 1; for each +1..+6 go to dest (board or self).
        - Return steps to n^2 else -1.

        Complexity: O(n^2) time/space.
        """
        n = len(board)

        def label_to_rc(label: int):
            r = n - 1 - (label - 1) // n
            c = (label - 1) % n
            if ((n - 1 - r) % 2) == 1:
                c = n - 1 - c
            return r, c

        target = n * n
        q = deque([(1, 0)])
        seen = {1}
        while q:
            cur, steps = q.popleft()
            if cur == target:
                return steps
            for nxt in range(cur + 1, min(cur + 6, target) + 1):
                r, c = label_to_rc(nxt)
                dest = board[r][c] if board[r][c] != -1 else nxt
                if dest not in seen:
                    seen.add(dest)
                    q.append((dest, steps + 1))
        return -1
# @lc code=end

