#
# @lc app=leetcode id=3186 lang=python3
#
# [3186] Maximum Total Damage With Spell Casting
#
# https://leetcode.com/problems/maximum-total-damage-with-spell-casting/description/
#
# algorithms
# Medium (45.02%)
# Likes:    765
# Dislikes: 65
# Total Accepted:    116.5K
# Total Submissions: 258.9K
# Testcase Example:  "[1,1,3,4]"
#
#
# A magician has various spells.
#
# You are given an array power, where each element represents the damage
# of a spell. Multiple spells can have the same damage value.
#
# It is a known fact that if a magician decides to cast a spell with a
# damage of power[i], they cannot cast any spell with a damage of power[i]
# - 2, power[i] - 1, power[i] + 1, or power[i] + 2.
#
# Each spell can be cast only once.
#
# Return the maximum possible total damage that a magician can cast.
#
# Example 1:
#
# Input: power = [1,1,3,4]
#
# Output: 6
#
# Explanation:
#
# The maximum possible damage of 6 is produced by casting spells 0, 1, 3
# with damage 1, 1, 4.
#
# Example 2:
#
# Input: power = [7,1,6,6]
#
# Output: 13
#
# Explanation:
#
# The maximum possible damage of 13 is produced by casting spells 1, 2, 3
# with damage 1, 6, 6.
#
# Constraints:
#
# 1 <= power.length <= 10^5
#
# 1 <= power[i] <= 10^9
#

# @lc code=start

from typing import List
from collections import Counter


class Solution:
    def maximumTotalDamage(self, power: List[int]) -> int:
        """
        Interview explanation:
        Casting damage x forbids x-2..x+2 except x itself. Maximize total damage
        (multiples of same x may all be cast).

        Algorithm:
        - Count frequency; sort unique damages vals.
        - DP like house robber: for vals[i], take all copies if previous taken
          damage is <= vals[i]-3; else skip conflicting suffix via binary/walk.

        Complexity: O(n log n) time, O(n) space.
        """
        freq = Counter(power)
        vals = sorted(freq)
        m = len(vals)
        # dp[i] = max damage using vals[0..i]
        dp = [0] * m
        j = -1  # last index with vals[j] <= vals[i]-3
        for i, v in enumerate(vals):
            take = v * freq[v]
            while j + 1 < i and vals[j + 1] <= v - 3:
                j += 1
            if j >= 0:
                take += dp[j]
            skip = dp[i - 1] if i else 0
            dp[i] = max(skip, take)
        return dp[-1]

    def maximumTotalDamage_memo(self, power: List[int]) -> int:
        """
        Interview explanation:
        Top-down over sorted unique damages: take (jump past conflicts) or skip.

        Algorithm:
        - Recurse on index i; if take, next index with vals[k] >= vals[i]+3.

        Complexity: O(n log n) time, O(n) space.
        """
        freq = Counter(power)
        vals = sorted(freq)
        m = len(vals)
        memo = [-1] * m

        def dfs(i: int) -> int:
            if i >= m:
                return 0
            if memo[i] >= 0:
                return memo[i]
            skip = dfs(i + 1)
            k = i + 1
            while k < m and vals[k] - vals[i] <= 2:
                k += 1
            take = vals[i] * freq[vals[i]] + dfs(k)
            memo[i] = max(skip, take)
            return memo[i]

        return dfs(0)
# @lc code=end
