#
# @lc app=leetcode id=2572 lang=python3
#
# [2572] Count the Number of Square-Free Subsets
#
# https://leetcode.com/problems/count-the-number-of-square-free-subsets/description/
#
# algorithms
# Medium (26.81%)
# Likes:    509
# Dislikes: 124
# Total Accepted:    14.5K
# Total Submissions: 54.2K
# Testcase Example:  "[3,4,4,5]"
#
# You are given a positive integer 0-indexed array nums.
#
# A subset of the array nums is square-free if the product of its elements is a
# square-free integer.
#
# A square-free integer is an integer that is divisible by no square number
# other than 1.
#
# Return the number of square-free non-empty subsets of the array nums. Since
# the answer may be too large, return it modulo 10^9 + 7.
#
# A non-empty subset of nums is an array that can be obtained by deleting some
# (possibly none but not all) elements from nums. Two subsets are different if
# and only if the chosen indices to delete are different.
#
#
#
# Example 1:
#
# Input: nums = [3,4,4,5]
# Output: 3
# Explanation: There are 3 square-free subsets in this example:
# - The subset consisting of the 0^th element [3]. The product of its elements
# is 3, which is a square-free integer.
# - The subset consisting of the 3^rd element [5]. The product of its elements
# is 5, which is a square-free integer.
# - The subset consisting of 0^th and 3^rd elements [3,5]. The product of its
# elements is 15, which is a square-free integer.
# It can be proven that there are no more than 3 square-free subsets in the
# given array.
#
# Example 2:
#
# Input: nums = [1]
# Output: 1
# Explanation: There is 1 square-free subset in this example:
# - The subset consisting of the 0^th element [1]. The product of its elements
# is 1, which is a square-free integer.
# It can be proven that there is no more than 1 square-free subset in the given
# array.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# 1 <= nums[i] <= 30
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def squareFreeSubsets(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count non-empty subsets whose product is square-free (no squared prime factor).
        Numbers in 1..30; use bitmask DP over the 10 primes <= 30.

        Algorithm:
        - Skip numbers divisible by 4,9,25,...; map remaining to prime bitmasks.
        - DP[mask] = ways to form that used-prime mask; multiply frequencies; handle 1s as 2^cnt.

        Complexity: O(n + 2^P * P) time with P=10, O(2^P) space.
        """
        MOD = 10**9 + 7
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        cnt = Counter(nums)
        # mask for each square-free number in 2..30
        masks = {}
        for x in range(2, 31):
            m = 0
            ok = True
            y = x
            for i, p in enumerate(primes):
                if y % p == 0:
                    y //= p
                    if y % p == 0:
                        ok = False
                        break
                    m |= 1 << i
            if ok and y == 1:
                masks[x] = m
        dp = [0] * (1 << 10)
        dp[0] = 1
        for x, m in masks.items():
            c = cnt[x]
            if not c:
                continue
            ndp = dp[:]
            for mask in range(1 << 10):
                if dp[mask] and (mask & m) == 0:
                    ndp[mask | m] = (ndp[mask | m] + dp[mask] * c) % MOD
            dp = ndp
        ones = pow(2, cnt[1], MOD)
        total = sum(dp) % MOD
        # multiply by ways to include any subset of 1s; subtract empty overall
        return (total * ones - 1) % MOD
# @lc code=end
