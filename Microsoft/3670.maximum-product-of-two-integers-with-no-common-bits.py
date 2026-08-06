#
# @lc app=leetcode id=3670 lang=python3
#
# [3670] Maximum Product of Two Integers With No Common Bits
#
# https://leetcode.com/problems/maximum-product-of-two-integers-with-no-common-bits/description/
#
# algorithms
# Medium (15.45%)
# Likes:    106
# Dislikes: 21
# Total Accepted:    12.1K
# Total Submissions: 78K
# Testcase Example:  "[1,2,3,4,5,6,7]"
#
#
# You are given an integer array nums.
#
# Your task is to find two distinct indices i and j such that the product
# nums[i] * nums[j] is maximized, and the binary representations of
# nums[i] and nums[j] do not share any common set bits.
#
# Return the maximum possible product of such a pair. If no such pair
# exists, return 0.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5,6,7]
#
# Output: 12
#
# Explanation:
#
# The best pair is 3 (011) and 4 (100). They share no set bits and 3 * 4 =
# 12.
#
# Example 2:
#
# Input: nums = [5,6,4]
#
# Output: 0
#
# Explanation:
#
# Every pair of numbers has at least one common set bit. Hence, the answer
# is 0.
#
# Example 3:
#
# Input: nums = [64,8,32]
#
# Output: 2048
#
# Explanation:
#
# No pair of numbers share a common bit, so the answer is the product of
# the two maximum elements, 64 and 32 (64 * 32 = 2048).
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Want max nums[i]*nums[j] with nums[i] & nums[j] == 0. After SOS DP,
        dp[mask] stores the largest value among nums that is a submask of mask,
        so for each x the best partner lives under the complementary mask.

        Algorithm:
        - Let L = bit_length(max(nums)); M = 2^L.
        - Initialize dp[x] = x for each x in nums.
        - Propagate: for each bit, dp[mask|bit] = max(dp[mask|bit], dp[mask]).
        - Answer max over x of x * dp[((1<<L)-1) ^ x] (0 if none).

        Complexity: O(L * 2^L + n) time and O(2^L) space, L <= 20.
        """
        L = max(nums).bit_length()
        M = 1 << L
        dp = [0] * M
        for x in nums:
            dp[x] = x
        for i in range(L):
            bit = 1 << i
            for mask in range(M):
                if mask & bit:
                    continue
                if dp[mask] > dp[mask | bit]:
                    dp[mask | bit] = dp[mask]
        full = M - 1
        ans = 0
        for x in nums:
            ans = max(ans, x * dp[full ^ x])
        return ans
# @lc code=end
