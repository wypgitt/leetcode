#
# @lc app=leetcode id=3539 lang=python3
#
# [3539] Find Sum of Array Product of Magical Sequences
#
# https://leetcode.com/problems/find-sum-of-array-product-of-magical-sequences/description/
#
# algorithms
# Hard (61.36%)
# Likes:    223
# Dislikes: 158
# Total Accepted:    53.2K
# Total Submissions: 86.7K
# Testcase Example:  "5\n5\n[1,10,100,10000,1000000]"
#
#
# You are given two integers, m and k, and an integer array nums.
#
# A sequence of integers seq is called magical if:
#
# seq has a size of m.
#
# 0 <= seq[i] < nums.length
#
# The binary representation of 2^seq[0] + 2^seq[1] + ... + 2^seq[m - 1]
# has k set bits.
#
# The array product of this sequence is defined as prod(seq) =
# (nums[seq[0]] * nums[seq[1]] * ... * nums[seq[m - 1]]).
#
# Return the sum of the array products for all valid magical sequences.
#
# Since the answer may be large, return it modulo 10^9 + 7.
#
# A set bit refers to a bit in the binary representation of a number that
# has a value of 1.
#
# Example 1:
#
# Input: m = 5, k = 5, nums = [1,10,100,10000,1000000]
#
# Output: 991600007
#
# Explanation:
#
# All permutations of [0, 1, 2, 3, 4] are magical sequences, each with an
# array product of 10^13.
#
# Example 2:
#
# Input: m = 2, k = 2, nums = [5,4,3,2,1]
#
# Output: 170
#
# Explanation:
#
# The magical sequences are [0, 1], [0, 2], [0, 3], [0, 4], [1, 0], [1,
# 2], [1, 3], [1, 4], [2, 0], [2, 1], [2, 3], [2, 4], [3, 0], [3, 1], [3,
# 2], [3, 4], [4, 0], [4, 1], [4, 2], and [4, 3].
#
# Example 3:
#
# Input: m = 1, k = 1, nums = [28]
#
# Output: 28
#
# Explanation:
#
# The only magical sequence is [0].
#
# Constraints:
#
# 1 <= k <= m <= 30
#
# 1 <= nums.length <= 50
#
# 1 <= nums[i] <= 10^8
#

# @lc code=start
import math
from functools import lru_cache
from typing import List


class Solution:
    def magicalSum(self, m: int, k: int, nums: List[int]) -> int:
        """
        Interview explanation:
        Sequences are multisets of indices of size m; 2^{idx} contributions add
        with carries, and we need exactly k set bits. DP over index, remaining
        picks, remaining bits, and current carry, weighting by C(remain, t)*nums[i]^t.

        Algorithm:
        - dp(rem_m, rem_k, i, carry): sum of products for unfinished sequences.
        - At nums[i], choose count t=0..rem_m; update carry and bit usage.
        - Base: rem_m==0 and rem_k == popcount(carry).

        Complexity: O(n * m^2 * k * m) roughly with carry ≤ m; memoized.
        """
        MOD = 10**9 + 7
        n = len(nums)

        @lru_cache(None)
        def dp(rem_m: int, rem_k: int, i: int, carry: int) -> int:
            if rem_m < 0 or rem_k < 0:
                return 0
            if rem_m == 0:
                return int(rem_k == carry.bit_count())
            if i == n:
                return 0
            res = 0
            for t in range(rem_m + 1):
                contrib = math.comb(rem_m, t) * pow(nums[i], t, MOD) % MOD
                new_carry = carry + t
                res = (
                    res
                    + dp(rem_m - t, rem_k - (new_carry % 2), i + 1, new_carry // 2)
                    * contrib
                ) % MOD
            return res

        return dp(m, k, 0, 0)
# @lc code=end
