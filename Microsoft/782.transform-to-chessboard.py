#
# @lc app=leetcode id=782 lang=python3
#
# [782] Transform to Chessboard
#
# https://leetcode.com/problems/transform-to-chessboard/description/
#
# algorithms
# Hard (51.58%)
# Likes:    374
# Dislikes: 313
# Total Accepted:    22.6K
# Total Submissions: 43.9K
# Testcase Example:  "[[0,1,1,0],[0,1,1,0],[1,0,0,1],[1,0,0,1]]"
#
# You are given an n x n binary grid board. In each move, you can swap any two
# rows with each other, or any two columns with each other.
#
# Return the minimum number of moves to transform the board into a chessboard
# board. If the task is impossible, return -1.
#
# A chessboard board is a board where no 0's and no 1's are 4-directionally
# adjacent.
#
# Example 1:
#
# Input: board = [[0,1,1,0],[0,1,1,0],[1,0,0,1],[1,0,0,1]]
# Output: 2
# Explanation: One potential sequence of moves is shown.
# The first move swaps the first and second column.
# The second move swaps the second and third row.
#
# Example 2:
#
# Input: board = [[0,1],[1,0]]
# Output: 0
# Explanation: Also note that the board with 0 in the top left corner, is also
# a valid chessboard.
#
# Example 3:
#
# Input: board = [[1,0],[1,0]]
# Output: -1
# Explanation: No matter what sequence of moves you make, you cannot end with a
# valid chessboard.
#
# Constraints:
#
# n == board.length
#
# n == board[i].length
#
# 2 <= n <= 30
#
# board[i][j] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def movesToChessboard(self, board: List[List[int]]) -> int:
        """
        Interview explanation:
        A board can become a chessboard iff rows/cols are only two complementary
        patterns with nearly equal 0/1 counts. Count how many rows (cols) need
        swapping to alternate; take min of two phase alignments when n even.

        Algorithm:
        - n = len(board). For any i,j: board[0][0]^board[0][j]^board[i][0]^board[i][j] == 0
          (row i is equal or complement of row 0). Else impossible.
        - rowSum = sum(board[0]); colSum = sum(board[i][0] for i).
          Must be n//2 or (n+1)//2.
        - rowSwap = count of board[0][j] != j%2; similarly colSwap.
        - If n odd: answer uses the even-parity alignment (rowSwap even).
          If n even: min(rowSwap, n-rowSwap)/2 + same for cols.

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(board)
        for i in range(n):
            for j in range(n):
                if board[0][0] ^ board[i][0] ^ board[0][j] ^ board[i][j]:
                    return -1

        row_sum = sum(board[0])
        col_sum = sum(board[i][0] for i in range(n))
        if not (n // 2 <= row_sum <= (n + 1) // 2):
            return -1
        if not (n // 2 <= col_sum <= (n + 1) // 2):
            return -1

        row_swap = sum(board[0][j] != j % 2 for j in range(n))
        col_swap = sum(board[i][0] != i % 2 for i in range(n))

        if n % 2:
            if row_swap % 2:
                row_swap = n - row_swap
            if col_swap % 2:
                col_swap = n - col_swap
        else:
            row_swap = min(row_swap, n - row_swap)
            col_swap = min(col_swap, n - col_swap)
        return (row_swap + col_swap) // 2
# @lc code=end

