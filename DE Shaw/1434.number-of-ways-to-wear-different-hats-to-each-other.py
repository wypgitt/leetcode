#
# @lc app=leetcode id=1434 lang=python3
#
# [1434] Number of Ways to Wear Different Hats to Each Other
#
# https://leetcode.com/problems/number-of-ways-to-wear-different-hats-to-each-other/description/
#
# algorithms
# Hard (46.51%)
# Likes:    972
# Dislikes: 12
# Total Accepted:    24.0K
# Total Submissions: 51.6K
# Testcase Example:  "[[3,4],[4,5],[5]]"
#
# There are n people and 40 types of hats labeled from 1 to 40.
#
# Given a 2D integer array hats, where hats[i] is a list of all hats preferred
# by the i^th person.
#
# Return the number of ways that n people can wear different hats from each
# other.
#
# Since the answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: hats = [[3,4],[4,5],[5]]
# Output: 1
# Explanation: There is only one way to choose hats given the conditions.
# First person chooses hat 3, Second person chooses hat 4 and last one hat 5.
#
# Example 2:
#
# Input: hats = [[3,5,1],[3,5]]
# Output: 4
# Explanation: There are 4 ways to choose hats:
# (3,5), (5,3), (1,3) and (1,5)
#
# Example 3:
#
# Input: hats = [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]
# Output: 24
# Explanation: Each person can choose hats labeled from 1 to 4.
# Number of Permutations of (1,2,3,4) = 24.
#
# Constraints:
#
# n == hats.length
#
# 1 <= n <= 10
#
# 1 <= hats[i].length <= 40
#
# 1 <= hats[i][j] <= 40
#
# hats[i] contains a list of unique integers.
#

# @lc code=start
from typing import List
from functools import lru_cache
from collections import defaultdict


class Solution:
    def numberWays(self, hats: List[List[int]]) -> int:
        """
        Interview explanation:
        n people (n<=40), hats 1..40; each person has preferred hats; assign
        distinct hats. DP over people mask is 2^40 too big — instead DP over
        hat id and bitmask of assigned people (n<=10): dp[hat][mask].

        Algorithm:
        (DP hats × people-mask)
        - hat_to_people lists; dfs(hat, mask): skip hat or assign to free person who likes it.
        - Start dfs(1,0); done when mask full.

        Complexity: O(40 * 2^n * n) time, O(40 * 2^n) space.
        """
        MOD = 10**9 + 7
        n = len(hats)
        hat_people = defaultdict(list)
        for p, pref in enumerate(hats):
            for h in pref:
                hat_people[h].append(p)
        full = (1 << n) - 1

        @lru_cache(None)
        def dfs(h: int, mask: int) -> int:
            if mask == full:
                return 1
            if h > 40:
                return 0
            ans = dfs(h + 1, mask)  # skip this hat
            for p in hat_people[h]:
                if (mask >> p) & 1 == 0:
                    ans = (ans + dfs(h + 1, mask | (1 << p))) % MOD
            return ans

        return dfs(1, 0)

    def numberWays_iter(self, hats: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate bottom-up DP: dp[mask] ways; iterate hats, update new masks.

        Algorithm:
        - dp[0]=1; for each hat, for masks descending/copy, assign people.

        Complexity: O(40 * 2^n * n) time, O(2^n) space.
        """
        MOD = 10**9 + 7
        n = len(hats)
        hat_people = [[] for _ in range(41)]
        for p, pref in enumerate(hats):
            for h in pref:
                hat_people[h].append(p)
        dp = [0] * (1 << n)
        dp[0] = 1
        for h in range(1, 41):
            ndp = dp[:]
            for mask in range(1 << n):
                if dp[mask] == 0:
                    continue
                for p in hat_people[h]:
                    if (mask >> p) & 1 == 0:
                        nmask = mask | (1 << p)
                        ndp[nmask] = (ndp[nmask] + dp[mask]) % MOD
            dp = ndp
        return dp[(1 << n) - 1]
# @lc code=end
