#
# @lc app=leetcode id=3671 lang=python3
#
# [3671] Sum of Beautiful Subsequences
#
# https://leetcode.com/problems/sum-of-beautiful-subsequences/description/
#
# algorithms
# Hard (31.03%)
# Likes:    39
# Dislikes: 5
# Total Accepted:    9.3K
# Total Submissions: 29.9K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an integer array nums of length n.
#
# For every positive integer g, we define the beauty of g as the product
# of g and the number of strictly increasing subsequences of nums whose
# greatest common divisor (GCD) is exactly g.
#
# Return the sum of beauty values for all positive integers g.
#
# Since the answer could be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: 10
#
# Explanation:
#
# All strictly increasing subsequences and their GCDs are:
#
#                         Subsequence
#                         GCD
#
#                         [1]
#                         1
#
#                         [2]
#                         2
#
#                         [3]
#                         3
#
#                         [1,2]
#                         1
#
#                         [1,3]
#                         1
#
#                         [2,3]
#                         1
#
#                         [1,2,3]
#                         1
#
# Calculating beauty for each GCD:
#
#                         GCD
#                         Count of subsequences
#                         Beauty (GCD × Count)
#
#                         1
#                         5
#                         1 × 5 = 5
#
#                         2
#                         1
#                         2 × 1 = 2
#
#                         3
#                         1
#                         3 × 1 = 3
#
# Total beauty is 5 + 2 + 3 = 10.
#
# Example 2:
#
# Input: nums = [4,6]
#
# Output: 12
#
# Explanation:
#
# All strictly increasing subsequences and their GCDs are:
#
#                         Subsequence
#                         GCD
#
#                         [4]
#                         4
#
#                         [6]
#                         6
#
#                         [4,6]
#                         2
#
# Calculating beauty for each GCD:
#
#                         GCD
#                         Count of subsequences
#                         Beauty (GCD × Count)
#
#                         2
#                         1
#                         2 × 1 = 2
#
#                         4
#                         1
#                         4 × 1 = 4
#
#                         6
#                         1
#                         6 × 1 = 6
#
# Total beauty is 2 + 4 + 6 = 12.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^4
#
# 1 <= nums[i] <= 7 * 10^4
#

# @lc code=start
from typing import List


class Solution:
    def totalBeauty(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Beauty(g) = g * (# strictly increasing subsequences with gcd == g).
        Count subsequences whose values are all multiples of g (via Fenwick on
        the filtered sequence), then Möbius-subtract multiples to get exact gcd.

        Algorithm:
        - For each g, collect nums divisible by g (order preserved).
        - Count strictly increasing subsequences with a Fenwick tree on compressed
          ranks: ways ending at x = 1 + sum(ways with rank < rank(x)).
        - Process g from large to small: F[g] = cnt[g] - sum F[2g] - F[3g] - ...
        - Answer sum g * F[g] mod 10^9+7.

        Complexity: O(U log U + n * d(max) * log n) with U = max(nums).
        """
        MOD = 10**9 + 7
        mx = max(nums)
        lookup: List[List[int]] = [[] for _ in range(mx + 1)]
        for x in nums:
            d = 1
            while d * d <= x:
                if x % d == 0:
                    lookup[d].append(x)
                    if d != x // d:
                        lookup[x // d].append(x)
                d += 1

        class BIT:
            def __init__(self, n: int) -> None:
                self.n = n
                self.bit = [0] * (n + 1)

            def add(self, i: int, v: int) -> None:
                i += 1
                while i <= self.n:
                    self.bit[i] = (self.bit[i] + v) % MOD
                    i += i & -i

            def query(self, i: int) -> int:
                if i < 0:
                    return 0
                i += 1
                s = 0
                while i > 0:
                    s = (s + self.bit[i]) % MOD
                    i -= i & -i
                return s

        def count_inc(arr: List[int]) -> int:
            if not arr:
                return 0
            vals = sorted(set(arr))
            rank = {v: i for i, v in enumerate(vals)}
            bit = BIT(len(vals))
            for x in arr:
                r = rank[x]
                ways = (bit.query(r - 1) + 1) % MOD
                bit.add(r, ways)
            return bit.query(len(vals) - 1)

        f = [0] * (mx + 1)
        ans = 0
        for g in range(mx, 0, -1):
            if not lookup[g]:
                continue
            f[g] = count_inc(lookup[g])
            for ng in range(g + g, mx + 1, g):
                f[g] = (f[g] - f[ng]) % MOD
            ans = (ans + g * f[g]) % MOD
        return ans
# @lc code=end
