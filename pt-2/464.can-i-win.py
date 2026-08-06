#
# @lc app=leetcode id=464 lang=python3
#
# [464] Can I Win
#
# https://leetcode.com/problems/can-i-win/description/
#
# algorithms
# Medium (31.37%)
# Likes:    2837
# Dislikes: 433
# Total Accepted:    123.8K
# Total Submissions: 394.8K
# Testcase Example:  '10\n11'
#
# In the "100 game" two players take turns adding, to a running total, any
# integer from 1 to 10. The player who first causes the running total to reach
# or exceed 100 wins.
# 
# What if we change the game so that players cannot re-use integers?
# 
# For example, two players might take turns drawing from a common pool of
# numbers from 1 to 15 without replacement until they reach a total >= 100.
# 
# Given two integers maxChoosableInteger and desiredTotal, return true if the
# first player to move can force a win, otherwise, return false. Assume both
# players play optimally.
# 
# 
# Example 1:
# 
# 
# Input: maxChoosableInteger = 10, desiredTotal = 11
# Output: false
# Explanation:
# No matter which integer the first player choose, the first player will lose.
# The first player can choose an integer from 1 up to 10.
# If the first player choose 1, the second player can only choose integers from
# 2 up to 10.
# The second player will win by choosing 10 and get a total = 11, which is >=
# desiredTotal.
# Same with other integers chosen by the first player, the second player will
# always win.
# 
# 
# Example 2:
# 
# 
# Input: maxChoosableInteger = 10, desiredTotal = 0
# Output: true
# 
# 
# Example 3:
# 
# 
# Input: maxChoosableInteger = 10, desiredTotal = 1
# Output: true
# 
# 
# 
# Constraints:
# 
# 
# 1 <= maxChoosableInteger <= 20
# 0 <= desiredTotal <= 300
# 
# 
#

# @lc code=start
from functools import lru_cache


class Solution:
    def canIWin(self, maxChoosableInteger: int, desiredTotal: int) -> bool:
        if desiredTotal <= 0:
            return True
        if maxChoosableInteger * (maxChoosableInteger + 1) // 2 < desiredTotal:
            return False

        @lru_cache(None)
        def winning(used_mask: int, remaining: int) -> bool:
            for x in range(1, maxChoosableInteger + 1):
                bit = 1 << (x - 1)
                if used_mask & bit:
                    continue
                if x >= remaining or not winning(used_mask | bit, remaining - x):
                    return True
            return False

        return winning(0, desiredTotal)
# @lc code=end

"""
Interview explanation:
This is a finite two-player game with perfect information. A state is fully described by which numbers have been used and the remaining total needed. The current player wins if they can pick a number that either reaches the target immediately or leaves the opponent in a losing state.

Data structure: a bitmask compactly represents used numbers; memoized DFS avoids recomputing game states.

Edge cases: if the total of all numbers is smaller than desiredTotal, nobody can win. If desiredTotal <= 0, the first player has already satisfied the condition.

Complexity: there are at most 2^m masks and each tries up to m choices, so time is O(m * 2^m) and space is O(2^m), where m is maxChoosableInteger.
"""
