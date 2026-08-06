#
# @lc app=leetcode id=1690 lang=python3
#
# [1690] Stone Game VII
#
# https://leetcode.com/problems/stone-game-vii/description/
#
# algorithms
# Medium (58.99%)
# Likes:    1059
# Dislikes: 175
# Total Accepted:    45.8K
# Total Submissions: 77.6K
# Testcase Example:  "[5,3,1,4,2]"
#
# Alice and Bob take turns playing a game, with Alice starting first.
#
# There are n stones arranged in a row. On each player's turn, they can remove
# either the leftmost stone or the rightmost stone from the row and receive
# points equal to the sum of the remaining stones' values in the row. The
# winner is the one with the higher score when there are no stones left to
# remove.
#
# Bob found that he will always lose this game (poor Bob, he always loses), so
# he decided to minimize the score's difference. Alice's goal is to maximize
# the difference in the score.
#
# Given an array of integers stones where stones[i] represents the value of the
# i^th stone from the left, return the difference in Alice and Bob's score if
# they both play optimally.
#
# Example 1:
#
# Input: stones = [5,3,1,4,2]
# Output: 6
# Explanation:
# - Alice removes 2 and gets 5 + 3 + 1 + 4 = 13 points. Alice = 13, Bob = 0,
# stones = [5,3,1,4].
# - Bob removes 5 and gets 3 + 1 + 4 = 8 points. Alice = 13, Bob = 8, stones =
# [3,1,4].
# - Alice removes 3 and gets 1 + 4 = 5 points. Alice = 18, Bob = 8, stones =
# [1,4].
# - Bob removes 1 and gets 4 points. Alice = 18, Bob = 12, stones = [4].
# - Alice removes 4 and gets 0 points. Alice = 18, Bob = 12, stones = [].
# The score difference is 18 - 12 = 6.
#
# Example 2:
#
# Input: stones = [7,90,5,1,100,10,10,2]
# Output: 122
#
# Constraints:
#
# n == stones.length
#
# 2 <= n <= 1000
#
# 1 <= stones[i] <= 1000
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def stoneGameVII(self, stones: List[int]) -> int:
        """
        Interview explanation:
        Players remove either end; score += sum of remaining. Maximize own-opponent
        difference. Interval DP: dp[i][j] = max score diff for stones[i..j] to move.

        Algorithm (DP):
        - prefix sums for range sum; dp[i][j] = max(sum(i+1..j)-dp[i+1][j],
          sum(i..j-1)-dp[i][j-1]) with opponent optimally.

        Complexity: O(n^2) time/space.
        """
        n = len(stones)
        pref = [0] * (n + 1)
        for i, v in enumerate(stones):
            pref[i + 1] = pref[i] + v

        def s(i, j):
            return pref[j + 1] - pref[i]

        dp = [[0] * n for _ in range(n)]
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                # take left stones[i]: score = s(i+1,j), then opponent gets dp[i+1][j]
                dp[i][j] = max(s(i + 1, j) - dp[i + 1][j], s(i, j - 1) - dp[i][j - 1])
        return dp[0][n - 1]

    def stoneGameVII_memo(self, stones: List[int]) -> int:
        """
        Interview explanation:
        Alternate top-down memo on (i,j) with prefix sums.

        Algorithm:
        - dfs(i,j)=max(sum(i+1,j)-dfs(i+1,j), sum(i,j-1)-dfs(i,j-1))

        Complexity: O(n^2) time/space.
        """
        n = len(stones)
        pref = [0] * (n + 1)
        for i, v in enumerate(stones):
            pref[i + 1] = pref[i] + v

        @lru_cache(None)
        def dfs(i, j):
            if i == j:
                return 0
            return max(
                pref[j + 1] - pref[i + 1] - dfs(i + 1, j),
                pref[j] - pref[i] - dfs(i, j - 1),
            )

        return dfs(0, n - 1)
# @lc code=end
