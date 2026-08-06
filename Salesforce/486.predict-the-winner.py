#
# @lc app=leetcode id=486 lang=python3
#
# [486] Predict the Winner
#
# https://leetcode.com/problems/predict-the-winner/description/
#
# algorithms
# Medium (59.81%)
# Likes:    6610
# Dislikes: 302
# Total Accepted:    412K
# Total Submissions: 689K
# Testcase Example:  "[1,5,2]"
#
# You are given an integer array nums. Two players are playing a game with this
# array: player 1 and player 2.
#
# Player 1 and player 2 take turns, with player 1 starting first. Both players
# start the game with a score of 0. At each turn, the player takes one of the
# numbers from either end of the array (i.e., nums[0] or nums[nums.length - 1])
# which reduces the size of the array by 1. The player adds the chosen number
# to their score. The game ends when there are no more elements in the array.
#
# Return true if Player 1 can win the game. If the scores of both players are
# equal, then player 1 is still the winner, and you should also return true.
# You may assume that both players are playing optimally.
#
# Example 1:
#
# Input: nums = [1,5,2]
# Output: false
# Explanation: Initially, player 1 can choose between 1 and 2.
# If he chooses 2 (or 1), then player 2 can choose from 1 (or 2) and 5. If
# player 2 chooses 5, then player 1 will be left with 1 (or 2).
# So, final score of player 1 is 1 + 2 = 3, and player 2 is 5.
# Hence, player 1 will never be the winner and you need to return false.
#
# Example 2:
#
# Input: nums = [1,5,233,7]
# Output: true
# Explanation: Player 1 first chooses 1. Then player 2 has to choose between 5
# and 7. No matter which number player 2 choose, player 1 can choose 233.
# Finally, player 1 has more score (234) than player 2 (12), so you need to
# return True representing player1 can win.
#
# Constraints:
#
# 1 <= nums.length <= 20
#
# 0 <= nums[i] <= 10^7
#

# @lc code=start
from typing import List


class Solution:
    def predictTheWinner(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Minimax / interval DP: players optimally take from ends. dp[i][j] =
        best score difference (current - opponent) on subarray i..j.
        Player 1 wins if dp[0][n-1] >= 0.

        Algorithm:
        - dp[i][i] = nums[i]
        - dp[i][j] = max(nums[i] - dp[i+1][j], nums[j] - dp[i][j-1])
        - Return dp[0][n-1] >= 0.

        Complexity: O(n^2) time and space.
        """
        n = len(nums)
        dp = [[0] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = nums[i]
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                dp[i][j] = max(nums[i] - dp[i + 1][j], nums[j] - dp[i][j - 1])
        return dp[0][n - 1] >= 0

    def predictTheWinner_minimax(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: recursive minimax with memo — maximizer of score difference
        choosing left or right end each turn.

        Complexity: O(n^2) with memo, O(n^2) space.
        """
        from functools import lru_cache

        @lru_cache(None)
        def diff(i: int, j: int) -> int:
            if i == j:
                return nums[i]
            return max(nums[i] - diff(i + 1, j), nums[j] - diff(i, j - 1))

        return diff(0, len(nums) - 1) >= 0
# @lc code=end
