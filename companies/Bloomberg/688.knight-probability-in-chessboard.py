#
# @lc app=leetcode id=688 lang=python3
#
# [688] Knight Probability in Chessboard
#
# https://leetcode.com/problems/knight-probability-in-chessboard/description/
#
# algorithms
# Medium (57.23%)
# Likes:    4062
# Dislikes: 498
# Total Accepted:    189K
# Total Submissions: 331K
# Testcase Example:  "3"
#
# On an n x n chessboard, a knight starts at the cell (row, column) and
# attempts to make exactly k moves. The rows and columns are 0-indexed, so the
# top-left cell is (0, 0), and the bottom-right cell is (n - 1, n - 1).
#
# A chess knight has eight possible moves it can make, as illustrated below.
# Each move is two cells in a cardinal direction, then one cell in an
# orthogonal direction.
#
# Each time the knight is to move, it chooses one of eight possible moves
# uniformly at random (even if the piece would go off the chessboard) and moves
# there.
#
# The knight continues moving until it has made exactly k moves or has moved
# off the chessboard.
#
# Return the probability that the knight remains on the board after it has
# stopped moving.
#
# Example 1:
#
# Input: n = 3, k = 2, row = 0, column = 0
# Output: 0.06250
# Explanation: There are two moves (to (1,2), (2,1)) that will keep the knight
# on the board.
# From each of those positions, there are also two moves that will keep the
# knight on the board.
# The total probability the knight stays on the board is 0.0625.
#
# Example 2:
#
# Input: n = 1, k = 0, row = 0, column = 0
# Output: 1.00000
#
# Constraints:
#
# 1 <= n <= 25
#
# 0 <= k <= 100
#
# 0 <= row, column <= n - 1
#

# @lc code=start
class Solution:
    def knightProbability(self, n: int, k: int, row: int, column: int) -> float:
        """
        Interview explanation:
        Knight moves uniformly to 8 positions; probability of still on board
        after k moves. DP: dp[steps][r][c] or rolling 2D — sum of probabilities
        flowing into each cell from previous step / 8.

        Algorithm:
        - Start dp[row][col]=1. For each of k steps, compute next board:
          for each cell with p>0, add p/8 to each valid knight landing.
        - Answer = sum of final board.

        Complexity: O(k * n^2) time, O(n^2) space.
        """
        if k == 0:
            return 1.0
        dirs = (
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2),
        )
        dp = [[0.0] * n for _ in range(n)]
        dp[row][column] = 1.0
        for _ in range(k):
            nxt = [[0.0] * n for _ in range(n)]
            for r in range(n):
                for c in range(n):
                    if dp[r][c] == 0:
                        continue
                    for dr, dc in dirs:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < n and 0 <= nc < n:
                            nxt[nr][nc] += dp[r][c] / 8.0
            dp = nxt
        return sum(sum(row) for row in dp)
# @lc code=end
