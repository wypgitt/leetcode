#
# @lc app=leetcode id=51 lang=python3
#
# [51] N-Queens
#
# https://leetcode.com/problems/n-queens/description/
#
# algorithms
# Hard (76.19%)
# Likes:    14612
# Dislikes: 356
# Total Accepted:    1.4M
# Total Submissions: 1.8M
# Testcase Example:  "4"
#
# The n-queens puzzle is the problem of placing n queens on an n x n chessboard
# such that no two queens attack each other.
#
# Given an integer n, return all distinct solutions to the n-queens puzzle. You
# may return the answer in any order.
#
# Each solution contains a distinct board configuration of the n-queens'
# placement, where 'Q' and '.' both indicate a queen and an empty space,
# respectively.
#
# Example 1:
#
# Input: n = 4
# Output: [[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]
# Explanation: There exist two distinct solutions to the 4-queens puzzle as
# shown above
#
# Example 2:
#
# Input: n = 1
# Output: [["Q"]]
#
# Constraints:
#
# 1 <= n <= 9
#

# @lc code=start
from typing import List


class Solution:
    def solveNQueens(self, n: int) -> List[List[str]]:
        """
        Interview explanation:
        Place one queen per row. Columns and both diagonals are tracked with
        sets so conflict checks are O(1). Diagonals are keyed by (row-col) and
        (row+col).

        Algorithm:
        - Backtrack row by row; try each free column.
        - On placing a queen, mark col, diag, anti-diag; recurse to next row.
        - At row == n, record the board configuration.

        Complexity: O(n!) time, O(n) extra space excluding output.
        """
        board = [["."] * n for _ in range(n)]
        cols: set[int] = set()
        diag: set[int] = set()
        anti: set[int] = set()
        ans: List[List[str]] = []

        def backtrack(row: int) -> None:
            if row == n:
                ans.append(["".join(r) for r in board])
                return
            for col in range(n):
                if col in cols or (row - col) in diag or (row + col) in anti:
                    continue
                board[row][col] = "Q"
                cols.add(col)
                diag.add(row - col)
                anti.add(row + col)
                backtrack(row + 1)
                board[row][col] = "."
                cols.remove(col)
                diag.remove(row - col)
                anti.remove(row + col)

        backtrack(0)
        return ans
# @lc code=end
