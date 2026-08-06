#
# @lc app=leetcode id=3257 lang=python3
#
# [3257] Maximum Value Sum by Placing Three Rooks II
#
# https://leetcode.com/problems/maximum-value-sum-by-placing-three-rooks-ii/description/
#
# algorithms
# Hard (27.07%)
# Likes:    61
# Dislikes: 10
# Total Accepted:    5.8K
# Total Submissions: 21.3K
# Testcase Example:  "[[-3,1,1,1],[-3,1,-3,1],[-3,2,1,1]]"
#
#
# You are given a m x n 2D array board representing a chessboard, where
# board[i][j] represents the value of the cell (i, j).
#
# Rooks in the same row or column attack each other. You need to place
# three rooks on the chessboard such that the rooks do not attack each
# other.
#
# Return the maximum sum of the cell values on which the rooks are placed.
#
# Example 1:
#
# Input: board = [[-3,1,1,1],[-3,1,-3,1],[-3,2,1,1]]
#
# Output: 4
#
# Explanation:
#
# We can place the rooks in the cells (0, 2), (1, 3), and (2, 1) for a sum
# of 1 + 1 + 2 = 4.
#
# Example 2:
#
# Input: board = [[1,2,3],[4,5,6],[7,8,9]]
#
# Output: 15
#
# Explanation:
#
# We can place the rooks in the cells (0, 0), (1, 1), and (2, 2) for a sum
# of 1 + 5 + 9 = 15.
#
# Example 3:
#
# Input: board = [[1,1,1],[1,1,1],[1,1,1]]
#
# Output: 3
#
# Explanation:
#
# We can place the rooks in the cells (0, 2), (1, 1), and (2, 0) for a sum
# of 1 + 1 + 1 = 3.
#
# Constraints:
#
# 3 <= m == board.length <= 500
#
# 3 <= n == board[i].length <= 500
#
# -10^9 <= board[i][j] <= 10^9
#

# @lc code=start
import heapq
import itertools
from typing import List


class Solution:
    def maximumValueSum(self, board: List[List[int]]) -> int:
        """
        Interview explanation:
        Same as Three Rooks I with larger board (500). Top-3-per-row/col
        intersection + top-9 enumeration stays O(mn).

        Algorithm:
        - Top 3 cells in each row and column; intersect; keep top 9.
        - Maximize sum over triples with distinct rows and columns.

        Complexity: O(mn) time, O(m+n) space.
        """
        rows = [
            heapq.nlargest(3, [(val, i, j) for j, val in enumerate(row)])
            for i, row in enumerate(board)
        ]
        cols = [
            heapq.nlargest(3, [(val, i, j) for i, val in enumerate(col)])
            for j, col in enumerate(zip(*board))
        ]
        top_nine = heapq.nlargest(
            9, set(itertools.chain.from_iterable(rows)) & set(itertools.chain.from_iterable(cols))
        )
        return max(
            val1 + val2 + val3
            for (val1, i1, j1), (val2, i2, j2), (val3, i3, j3) in itertools.combinations(
                top_nine, 3
            )
            if len({i1, i2, i3}) == 3 and len({j1, j2, j3}) == 3
        )
# @lc code=end
