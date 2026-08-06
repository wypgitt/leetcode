#
# @lc app=leetcode id=3360 lang=python3
#
# [3360] Stone Removal Game
#
# https://leetcode.com/problems/stone-removal-game/description/
#
# algorithms
# Easy (42.72%)
# Likes:    73
# Dislikes: 5
# Total Accepted:    35.6K
# Total Submissions: 83.2K
# Testcase Example:  "12"
#
#
# Alice and Bob are playing a game where they take turns removing stones
# from a pile, with Alice going first.
#
# Alice starts by removing exactly 10 stones on her first turn.
#
# For each subsequent turn, each player removes exactly 1 fewer stone than
# the previous opponent.
#
# The player who cannot make a move loses the game.
#
# Given a positive integer n, return true if Alice wins the game and false
# otherwise.
#
# Example 1:
#
# Input: n = 12
#
# Output: true
#
# Explanation:
#
# Alice removes 10 stones on her first turn, leaving 2 stones for Bob.
#
# Bob cannot remove 9 stones, so Alice wins.
#
# Example 2:
#
# Input: n = 1
#
# Output: false
#
# Explanation:
#
# Alice cannot remove 10 stones, so Alice loses.
#
# Constraints:
#
# 1 <= n <= 50
#

# @lc code=start

class Solution:
    def canAliceWin(self, n: int) -> bool:
        """
        Interview explanation:
        Alice removes 10, then players remove 9,8,... until a player cannot.
        Simulate the unique forced sequence.

        Algorithm:
        - remove = 10; while n >= remove: n -= remove; remove -= 1; switch player.
        - Alice wins iff the player who fails is Bob.

        Complexity: O(1) time (≤10 turns), O(1) space.
        """
        remove = 10
        alice_turn = True
        while n >= remove:
            n -= remove
            remove -= 1
            alice_turn = not alice_turn
        return not alice_turn

    def canAliceWin_math(self, n: int) -> bool:
        """
        Interview explanation:
        Alternate: total removed after t turns is 10+9+...+(11-t)= t*(21-t)/2.
        Find maximal t with that ≤ n; Alice wins on odd t.

        Algorithm:
        - Compute largest t with t*(21-t)/2 ≤ n; return t % 2 == 1.

        Complexity: O(1) time, O(1) space.
        """
        t = 0
        remove = 10
        while n >= remove:
            n -= remove
            remove -= 1
            t += 1
        return t % 2 == 1
# @lc code=end
