#
# @lc app=leetcode id=914 lang=python3
#
# [914] X of a Kind in a Deck of Cards
#
# https://leetcode.com/problems/x-of-a-kind-in-a-deck-of-cards/description/
#
# algorithms
# Easy (30.44%)
# Likes:    1913
# Dislikes: 584
# Total Accepted:    164K
# Total Submissions: 537K
# Testcase Example:  "[1,2,3,4,4,3,2,1]"
#
# You are given an integer array deck where deck[i] represents the number
# written on the i^th card.
#
# Partition the cards into one or more groups such that:
#
# Each group has exactly x cards where x > 1, and
#
# All the cards in one group have the same integer written on them.
#
# Return true if such partition is possible, or false otherwise.
#
# Example 1:
#
# Input: deck = [1,2,3,4,4,3,2,1]
# Output: true
# Explanation: Possible partition [1,1],[2,2],[3,3],[4,4].
#
# Example 2:
#
# Input: deck = [1,1,1,2,2,2,3,3]
# Output: false
# Explanation: No possible partition.
#
# Constraints:
#
# 1 <= deck.length <= 10^4
#
# 0 <= deck[i] < 10^4
#

# @lc code=start
from collections import Counter
from math import gcd
from typing import List
from functools import reduce


class Solution:
    def hasGroupsSizeX(self, deck: List[int]) -> bool:
        """
        Interview explanation:
        Partition into groups of size X>=2 with equal values. Possible iff
        gcd of all frequencies >= 2.

        Algorithm:
        - Count freqs; return gcd(all counts) >= 2.

        Complexity: O(n + log A) time, O(n) space.
        """
        cnt = Counter(deck)
        g = reduce(gcd, cnt.values())
        return g >= 2
# @lc code=end

