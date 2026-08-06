#
# @lc app=leetcode id=1510 lang=python3
#
# [1510] Stone Game IV
#
# https://leetcode.com/problems/stone-game-iv/description/
#
# algorithms
# Hard (59.64%)
# Likes:    1655
# Dislikes: 76
# Total Accepted:    86.1K
# Total Submissions: 144K
# Testcase Example:  "1"
#
# Alice and Bob take turns playing a game, with Alice starting first.
#
# Initially, there are n stones in a pile. On each player's turn, that player
# makes a move consisting of removing any non-zero square number of stones in
# the pile.
#
# Also, if a player cannot make a move, he/she loses the game.
#
# Given a positive integer n, return true if and only if Alice wins the game
# otherwise return false, assuming both players play optimally.
#
# Example 1:
#
# Input: n = 1
# Output: true
# Explanation: Alice can remove 1 stone winning the game because Bob doesn't
# have any moves.
#
# Example 2:
#
# Input: n = 2
# Output: false
# Explanation: Alice can only remove 1 stone, after that Bob removes the last
# one winning the game (2 -> 1 -> 0).
#
# Example 3:
#
# Input: n = 4
# Output: true
# Explanation: n is already a perfect square, Alice can win with one move,
# removing 4 stones (4 -> 0).
#
# Constraints:
#
# 1 <= n <= 10^5
#

# @lc code=start
class Solution:
    def winnerSquareGame(self, n: int) -> bool:
        """
        Interview explanation:
        Alice/Bob remove a square number of stones; can't move loses. DP:
        dp[i]=True if current player facing i stones can force a win — exists
        square s with s<=i and not dp[i-s].

        Algorithm:
        - dp[0]=False; for i=1..n: dp[i]=any(not dp[i-k*k] for k*k<=i).

        Complexity: O(n√n) time, O(n) space.
        """
        dp = [False] * (n + 1)
        for i in range(1, n + 1):
            k = 1
            while k * k <= i:
                if not dp[i - k * k]:
                    dp[i] = True
                    break
                k += 1
        return dp[n]

    def winnerSquareGame_memo(self, n: int) -> bool:
        """
        Interview explanation:
        Alternate top-down memo DFS: win(i) if exists square move to a losing
        position for the opponent.

        Algorithm:
        - @cache dfs(i): for k*k<=i if not dfs(i-k*k): True; else False.

        Complexity: O(n√n) time, O(n) space.
        """
        from functools import lru_cache

        @lru_cache(None)
        def dfs(i: int) -> bool:
            k = 1
            while k * k <= i:
                if not dfs(i - k * k):
                    return True
                k += 1
            return False

        return dfs(n)
# @lc code=end
