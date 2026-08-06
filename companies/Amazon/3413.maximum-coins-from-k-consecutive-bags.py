#
# @lc app=leetcode id=3413 lang=python3
#
# [3413] Maximum Coins From K Consecutive Bags
#
# https://leetcode.com/problems/maximum-coins-from-k-consecutive-bags/description/
#
# algorithms
# Medium (26.20%)
# Likes:    211
# Dislikes: 31
# Total Accepted:    11K
# Total Submissions: 42.1K
# Testcase Example:  "[[8,10,1],[1,3,2],[5,6,4]]\n4"
#
#
# There are an infinite amount of bags on a number line, one bag for each
# coordinate. Some of these bags contain coins.
#
# You are given a 2D array coins, where coins[i] = [l_i, r_i, c_i] denotes
# that every bag from l_i to r_i contains c_i coins.
#
# The segments that coins contain are non-overlapping.
#
# You are also given an integer k.
#
# Return the maximum amount of coins you can obtain by collecting k
# consecutive bags.
#
# Example 1:
#
# Input: coins = [[8,10,1],[1,3,2],[5,6,4]], k = 4
#
# Output: 10
#
# Explanation:
#
# Selecting bags at positions [3, 4, 5, 6] gives the maximum number of
# coins: 2 + 0 + 4 + 4 = 10.
#
# Example 2:
#
# Input: coins = [[1,10,3]], k = 2
#
# Output: 6
#
# Explanation:
#
# Selecting bags at positions [1, 2] gives the maximum number of coins: 3
# + 3 = 6.
#
# Constraints:
#
# 1 <= coins.length <= 10^5
#
# 1 <= k <= 10^9
#
# coins[i] == [l_i, r_i, c_i]
#
# 1 <= l_i <= r_i <= 10^9
#
# 1 <= c_i <= 1000
#
# The given segments are non-overlapping.
#

# @lc code=start
from typing import List


class Solution:
    def maximumCoins(self, coins: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Segments of equal coin density are disjoint. Optimal k-length
        window's left endpoint aligns with some segment start, or its
        right endpoint with some segment end (symmetric by negation).

        Algorithm:
        - Sort segments; for each start li, slide a window over [li, li+k)
          accumulating full segments plus a partial tail.
        - Repeat on negated coordinates for right-aligned windows.

        Complexity: O(n log n) time, O(n) space.
        """
        return max(
            self._slide([list(c) for c in coins], k),
            self._slide([[-r, -l, c] for l, r, c in coins], k),
        )

    def _slide(self, coins: List[List[int]], k: int) -> int:
        coins.sort()
        res = 0
        window_sum = 0
        j = 0
        n = len(coins)
        for li, ri, ci in coins:
            right_boundary = li + k
            while j + 1 < n and coins[j + 1][0] < right_boundary:
                lj, rj, cj = coins[j]
                window_sum += (rj - lj + 1) * cj
                j += 1
            last = 0
            if j < n and coins[j][0] < right_boundary:
                lj, rj, cj = coins[j]
                last = (min(right_boundary - 1, rj) - lj + 1) * cj
            res = max(res, window_sum + last)
            window_sum -= (ri - li + 1) * ci
        return res
# @lc code=end
