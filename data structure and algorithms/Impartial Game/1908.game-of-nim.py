#
# @lc app=leetcode id=1908 lang=python3
#
# [1908] Game of Nim
#
# https://leetcode.com/problems/game-of-nim/description/
#
# algorithms
# Medium (62.81%)
# Likes:    105
# Dislikes: 40
# Total Accepted:    5.4K
# Total Submissions: 8.5K
# Testcase Example:  "[1]"
#
#
# Alice and Bob take turns playing a game with Alice starting first.
#
# In this game, there are n piles of stones. On each player's turn, the
# player should remove any positive number of stones from a non-empty pile
# of his or her choice. The first player who cannot make a move loses, and
# the other player wins.
#
# Given an integer array piles, where piles[i] is the number of stones in
# the i^th pile, return true if Alice wins, or false if Bob wins.
#
# Both Alice and Bob play optimally.
#
# Example 1:
#
# Input: piles = [1]
# Output: true
# Explanation: There is only one possible scenario:
# - On the first turn, Alice removes one stone from the first pile. piles
# = [0].
# - On the second turn, there are no stones left for Bob to remove. Alice
# wins.
#
# Example 2:
#
# Input: piles = [1,1]
# Output: false
# Explanation: It can be proven that Bob will always win. One possible
# scenario is:
# - On the first turn, Alice removes one stone from the first pile. piles
# = [0,1].
# - On the second turn, Bob removes one stone from the second pile. piles
# = [0,0].
# - On the third turn, there are no stones left for Alice to remove. Bob
# wins.
#
# Example 3:
#
# Input: piles = [1,2,3]
# Output: false
# Explanation: It can be proven that Bob will always win. One possible
# scenario is:
# - On the first turn, Alice removes three stones from the third pile.
# piles = [1,2,0].
# - On the second turn, Bob removes one stone from the second pile. piles
# = [1,1,0].
# - On the third turn, Alice removes one stone from the first pile. piles
# = [0,1,0].
# - On the fourth turn, Bob removes one stone from the second pile. piles
# = [0,0,0].
# - On the fifth turn, there are no stones left for Alice to remove. Bob
# wins.
#
# Constraints:
#
# n == piles.length
#
# 1 <= n <= 7
#
# 1 <= piles[i] <= 7
#
# Follow-up: Could you find a linear time solution? Although the linear
# time solution may be beyond the scope of an interview, it could be
# interesting to know.
#
# @lc code=start
from typing import List
from functools import reduce
import operator


class Solution:
    def nimGame(self, piles: List[int]) -> bool:
        """
        Interview explanation:
        Premium Nim. Standard impartial game: first player wins iff XOR of all
        pile sizes is nonzero (Nim-sum / Sprague-Grundy for *n heaps).

        Algorithm:
        - Return XOR of all piles != 0.

        Complexity: O(n) time, O(1) space.
        """
        return reduce(operator.xor, piles, 0) != 0

    def nimGame_dp(self, piles: List[int]) -> bool:
        """
        Interview explanation:
        Alternate educational DP over multisets (only for tiny piles): a position
        is winning if some move leads to a losing position for opponent.

        Algorithm:
        - Memoize tuple(sorted piles); try decrementing each pile.

        Complexity: exponential without pruning; not for production.
        """
        from functools import lru_cache

        @lru_cache(None)
        def win(state):
            arr = list(state)
            for i, p in enumerate(arr):
                for take in range(1, p + 1):
                    nxt = arr[:]
                    nxt[i] = p - take
                    if not win(tuple(sorted(x for x in nxt if x > 0))):
                        return True
            return False

        return win(tuple(sorted(p for p in piles if p > 0)))
# @lc code=end
