#
# @lc app=leetcode id=1025 lang=python3
#
# [1025] Divisor Game
#
# https://leetcode.com/problems/divisor-game/description/
#
# algorithms
# Easy (72.36%)
# Likes:    2476
# Dislikes: 4213
# Total Accepted:    403K
# Total Submissions: 557K
# Testcase Example:  "2"
#
# Alice and Bob take turns playing a game, with Alice starting first.
#
# Initially, there is a number n on the chalkboard. On each player's turn, that
# player makes a move consisting of:
#
# Choosing any integer x with 0 < x < n and n % x == 0.
#
# Replacing the number n on the chalkboard with n - x.
#
# Also, if a player cannot make a move, they lose the game.
#
# Return true if and only if Alice wins the game, assuming both players play
# optimally.
#
# Example 1:
#
# Input: n = 2
# Output: true
# Explanation: Alice chooses 1, and Bob has no more moves.
#
# Example 2:
#
# Input: n = 3
# Output: false
# Explanation: Alice chooses 1, Bob chooses 1, and Alice has no more moves.
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start
class Solution:
    def divisorGame(self, n: int) -> bool:
        """
        Interview explanation:
        Math insight: first player wins iff n is even. From even you can always
        subtract 1 (choose x=1) leaving odd; from odd all moves leave even.
        Opponent then faces even and can always respond — inductively even wins.

        Algorithm:
        - Return n % 2 == 0

        Complexity: O(1) time and space.
        """
        return n % 2 == 0

    def divisorGame_dp(self, n: int) -> bool:
        """
        Interview explanation:
        Alternate classic DP: dp[i]=True if current player facing i can force a
        win — exists divisor x of i with not dp[i-x].

        Algorithm:
        - dp[0]=False; dp[1]=False
        - For i=2..n: for x|i and x<i: if not dp[i-x]: dp[i]=True

        Complexity: O(n * sqrt(n)) or O(n^2) naive, O(n) space.
        """
        dp = [False] * (n + 1)
        for i in range(2, n + 1):
            x = 1
            while x * x <= i:
                if i % x == 0:
                    if not dp[i - x]:
                        dp[i] = True
                        break
                    other = i // x
                    if other != i and other != x and not dp[i - other]:
                        dp[i] = True
                        break
                x += 1
        return dp[n]
# @lc code=end
