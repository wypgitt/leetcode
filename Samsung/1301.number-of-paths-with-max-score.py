#
# @lc app=leetcode id=1301 lang=python3
#
# [1301] Number of Paths with Max Score
#
# https://leetcode.com/problems/number-of-paths-with-max-score/description/
#
# algorithms
# Hard (63.65%)
# Likes:    782
# Dislikes: 41
# Total Accepted:    91.0K
# Total Submissions: 143K
# Testcase Example:  "[\"E3283\",\"47715\",\"31479\",\"X1X32\",\"721XS\"]"
#
# You are given a square board of characters. You can move on the board
# starting at the bottom right square marked with the character 'S'.
#
# You need to reach the top left square marked with the character 'E'. The rest
# of the squares are labeled either with a numeric character 1, 2, ..., 9 or
# with an obstacle 'X'. In one move you can go up, left or up-left (diagonally)
# only if there is no obstacle there.
#
# Return a list of two integers: the first integer is the maximum sum of
# numeric characters you can collect, and the second is the number of such
# paths that you can take to get that maximum sum, taken modulo 10^9 + 7.
#
# In case there is no path, return [0, 0].
#
# Example 1:
#
# Input: board = ["E23","2X2","12S"]
# Output: [7,1]
#
# Example 2:
#
# Input: board = ["E12","1X1","21S"]
# Output: [4,2]
#
# Example 3:
#
# Input: board = ["E11","XXX","11S"]
# Output: [0,0]
#
# Constraints:
#
# 2 <= board.length == board[i].length <= 100
#

# @lc code=start
from typing import List


class Solution:
    def pathsWithMaxScore(self, board: List[str]) -> List[int]:
        """
        Interview explanation:
        From 'S' (bottom-right) move only up/left/diagonal-up-left to 'E'.
        Collect digit scores; find max score and number of max-score paths mod 1e9+7.
        DP of (max_score, ways) from S toward E.

        Algorithm (DP):
        - Init S=(0,1). Scan cells reverse row/col; take max score over the three
          successors; sum ways for equal max. Digits add (E/S add 0).
        - Return dp[0][0] or [0,0] if unreachable.

        Complexity: O(n^2) time, O(n^2) space.
        """
        MOD = 10**9 + 7
        n = len(board)
        dp = [[(-1, 0) for _ in range(n)] for _ in range(n)]
        dp[n - 1][n - 1] = (0, 1)

        for r in range(n - 1, -1, -1):
            for c in range(n - 1, -1, -1):
                if board[r][c] == "X" or (r == n - 1 and c == n - 1):
                    continue
                best, ways = -1, 0
                for dr, dc in ((1, 0), (0, 1), (1, 1)):
                    nr, nc = r + dr, c + dc
                    if nr < n and nc < n:
                        s, w = dp[nr][nc]
                        if w == 0 or s < 0:
                            continue
                        if s > best:
                            best, ways = s, w
                        elif s == best:
                            ways = (ways + w) % MOD
                if best < 0:
                    continue
                add = 0 if board[r][c] in "ES" else int(board[r][c])
                dp[r][c] = (best + add, ways)

        score, ways = dp[0][0]
        return [0, 0] if ways == 0 else [score, ways]
# @lc code=end

