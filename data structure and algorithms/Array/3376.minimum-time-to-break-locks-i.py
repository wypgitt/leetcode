#
# @lc app=leetcode id=3376 lang=python3
#
# [3376] Minimum Time to Break Locks I
#
# https://leetcode.com/problems/minimum-time-to-break-locks-i/description/
#
# algorithms
# Medium (32.93%)
# Likes:    109
# Dislikes: 25
# Total Accepted:    14.8K
# Total Submissions: 44.9K
# Testcase Example:  "[3,4,1]\n1"
#
#
# Bob is stuck in a dungeon and must break n locks, each requiring some
# amount of energy to break. The required energy for each lock is stored
# in an array called strength where strength[i] indicates the energy
# needed to break the i^th lock.
#
# To break a lock, Bob uses a sword with the following characteristics:
#
# The initial energy of the sword is 0.
#
# The initial factor x by which the energy of the sword increases is 1.
#
# Every minute, the energy of the sword increases by the current factor x.
#
# To break the i^th lock, the energy of the sword must reach at least
# strength[i].
#
# After breaking a lock, the energy of the sword resets to 0, and the
# factor x increases by a given value k.
#
# Your task is to determine the minimum time in minutes required for Bob
# to break all n locks and escape the dungeon.
#
# Return the minimum time required for Bob to break all n locks.
#
# Example 1:
#
# Input: strength = [3,4,1], k = 1
#
# Output: 4
#
# Explanation:
#
#                         Time
#                         Energy
#                         x
#                         Action
#                         Updated x
#
#                         0
#                         0
#                         1
#                         Nothing
#                         1
#
#                         1
#                         1
#                         1
#                         Break 3^rd Lock
#                         2
#
#                         2
#                         2
#                         2
#                         Nothing
#                         2
#
#                         3
#                         4
#                         2
#                         Break 2^nd Lock
#                         3
#
#                         4
#                         3
#                         3
#                         Break 1^st Lock
#                         3
#
# The locks cannot be broken in less than 4 minutes; thus, the answer is
# 4.
#
# Example 2:
#
# Input: strength = [2,5,4], k = 2
#
# Output: 5
#
# Explanation:
#
#                         Time
#                         Energy
#                         x
#                         Action
#                         Updated x
#
#                         0
#                         0
#                         1
#                         Nothing
#                         1
#
#                         1
#                         1
#                         1
#                         Nothing
#                         1
#
#                         2
#                         2
#                         1
#                         Break 1^st Lock
#                         3
#
#                         3
#                         3
#                         3
#                         Nothing
#                         3
#
#                         4
#                         6
#                         3
#                         Break 2^n^d Lock
#                         5
#
#                         5
#                         5
#                         5
#                         Break 3^r^d Lock
#                         7
#
# The locks cannot be broken in less than 5 minutes; thus, the answer is
# 5.
#
# Constraints:
#
# n == strength.length
#
# 1 <= n <= 8
#
# 1 <= k <= 10
#
# 1 <= strength[i] <= 10^6
#

# @lc code=start
from typing import List
from functools import cache


class Solution:
    def findMinimumTime(self, strength: List[int], k: int) -> int:
        """
        Interview explanation:
        Order of breaking locks matters; factor x grows by k after each break.
        n <= 8 => bitmask DP over the set of broken locks.

        Algorithm:
        - dp(mask) = min extra minutes to finish from this broken set.
        - x = 1 + k * popcount(mask); time for lock i is ceil(strength[i] / x).

        Complexity: O(n * 2^n) time, O(2^n) space.
        """
        n = len(strength)
        inf = 10**18

        @cache
        def dp(mask: int) -> int:
            if mask == (1 << n) - 1:
                return 0
            x = 1 + k * mask.bit_count()
            best = inf
            for i in range(n):
                if (mask >> i) & 1 == 0:
                    t = (strength[i] + x - 1) // x
                    best = min(best, t + dp(mask | (1 << i)))
            return best

        return dp(0)
# @lc code=end
