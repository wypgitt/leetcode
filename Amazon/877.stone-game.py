#
# @lc app=leetcode id=877 lang=python3
#
# [877] Stone Game
#
# https://leetcode.com/problems/stone-game/description/
#
# algorithms
# Medium (76.81%)
# Likes:    3841
# Dislikes: 2987
# Total Accepted:    504K
# Total Submissions: 656K
# Testcase Example:  "[5,3,4,5]"
#
# Alice and Bob play a game with piles of stones. There are an even number of
# piles arranged in a row, and each pile has a positive integer number of
# stones piles[i].
#
# The objective of the game is to end with the most stones. The total number of
# stones across all the piles is odd, so there are no ties.
#
# Alice and Bob take turns, with Alice starting first. Each turn, a player
# takes the entire pile of stones either from the beginning or from the end of
# the row. This continues until there are no more piles left, at which point
# the person with the most stones wins.
#
# Assuming Alice and Bob play optimally, return true if Alice wins the game, or
# false if Bob wins.
#
# Example 1:
#
# Input: piles = [5,3,4,5]
# Output: true
# Explanation:
# Alice starts first, and can only take the first 5 or the last 5.
# Say she takes the first 5, so that the row becomes [3, 4, 5].
# If Bob takes 3, then the board is [4, 5], and Alice takes 5 to win with 10
# points.
# If Bob takes the last 5, then the board is [3, 4], and Alice takes 4 to win
# with 9 points.
# This demonstrated that taking the first 5 was a winning move for Alice, so we
# return true.
#
# Example 2:
#
# Input: piles = [3,7,2,3]
# Output: true
#
# Constraints:
#
# 2 <= piles.length <= 500
#
# piles.length is even.
#
# 1 <= piles[i] <= 500
#
# sum(piles[i]) is odd.
#

# @lc code=start
from typing import List


class Solution:
    def stoneGame(self, piles: List[int]) -> bool:
        """
        Interview explanation:
        Alice always wins optimally on even-length piles: she can always take
        the larger of (sum of even indices, sum of odd indices). Math shortcut.

        Algorithm (always-true math):
        - Return True (Alice wins for all valid inputs).

        Complexity: O(1) time/space.
        """
        return True

    def stoneGame_dp(self, piles: List[int]) -> bool:
        """
        Interview explanation:
        Alternate classic DP: dp[i][j] = best score difference (first-second)
        on subarray piles[i..j]. First player takes piles[i] or piles[j] and
        subtracts opponent's best on the remainder.

        Algorithm:
        - dp[i][i]=piles[i].
        - dp[i][j]=max(piles[i]-dp[i+1][j], piles[j]-dp[i][j-1]).
        - Alice wins if dp[0][n-1]>0.

        Complexity: O(n^2) time/space.
        """
        n = len(piles)
        dp = [[0] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = piles[i]
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                dp[i][j] = max(piles[i] - dp[i + 1][j], piles[j] - dp[i][j - 1])
        return dp[0][n - 1] > 0
# @lc code=end

