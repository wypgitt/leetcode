#
# @lc app=leetcode id=3757 lang=python3
#
# [3757] Number of Effective Subsequences
#
# https://leetcode.com/problems/number-of-effective-subsequences/description/
#
# algorithms
# Hard (33.01%)
# Likes:    33
# Dislikes: 2
# Total Accepted:    3.3K
# Total Submissions: 9.9K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an integer array nums.
#
# The strength of the array is defined as the bitwise OR of all its
# elements.
#
# A subsequence is considered effective if removing that subsequence
# strictly decreases the strength of the remaining elements.
#
# Return the number of effective subsequences in nums. Since the answer
# may be large, return it modulo 10^9 + 7.
#
# The bitwise OR of an empty array is 0.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: 3
#
# Explanation:
#
# The Bitwise OR of the array is 1 OR 2 OR 3 = 3.
#
# Subsequences that are effective are:
#
# [1, 3]: The remaining element [2] has a Bitwise OR of 2.
#
# [2, 3]: The remaining element [1] has a Bitwise OR of 1.
#
# [1, 2, 3]: The remaining elements [] have a Bitwise OR of 0.
#
# Thus, the total number of effective subsequences is 3.
#
# Example 2:
#
# Input: nums = [7,4,6]
#
# Output: 4
#
# Explanation:​​​​​​​
#
# The Bitwise OR of the array is 7 OR 4 OR 6 = 7.
#
# Subsequences that are effective are:
#
# [7]: The remaining elements [4, 6] have a Bitwise OR of 6.
#
# [7, 4]: The remaining element [6] has a Bitwise OR of 6.
#
# [7, 6]: The remaining element [4] has a Bitwise OR of 4.
#
# [7, 4, 6]: The remaining elements [] have a Bitwise OR of 0.
#
# Thus, the total number of effective subsequences is 4.
#
# Example 3:
#
# Input: nums = [8,8]
#
# Output: 1
#
# Explanation:
#
# The Bitwise OR of the array is 8 OR 8 = 8.
#
# Only the subsequence [8, 8] is effective since removing it leaves []
# which has a Bitwise OR of 0.
#
# Thus, the total number of effective subsequences is 1.
#
# Example 4:
#
# Input: nums = [2,2,1]
#
# Output: 5
#
# Explanation:
#
# The Bitwise OR of the array is 2 OR 2 OR 1 = 3.
#
# Subsequences that are effective are:
#
# [1]: The remaining elements [2, 2] have a Bitwise OR of 2.
#
# [2, 1] (using nums[0], nums[2]): The remaining element [2] has a Bitwise
# OR of 2.
#
# [2, 1] (using nums[1], nums[2]): The remaining element [2] has a Bitwise
# OR of 2.
#
# [2, 2]: The remaining element [1] has a Bitwise OR of 1.
#
# [2, 2, 1]: The remaining elements [] have a Bitwise OR of 0.
#
# Thus, the total number of effective subsequences is 5.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def countEffective(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Strength = OR of all elements. Removing a subsequence is effective iff the
        OR of the kept elements is a proper submask of the total OR (some bit lost).

        Algorithm:
        - Compress bits of total OR. SOS-DP: dp[mask] = #elements that are submasks
          of mask.
        - Inclusion-exclusion over nonempty lost-bit sets: sum (-1)^{|T|+1}
          * 2^{#elems missing all bits in T}.

        Complexity: O((n + 2^b) b) time, O(2^b) space, b = popcount(OR) <= 20.
        """
        MOD = 10**9 + 7
        total = 0
        for x in nums:
            total |= x
        bits = [i for i in range(total.bit_length()) if total & (1 << i)]
        b = len(bits)
        dp = [0] * (1 << b)
        for x in nums:
            mask = 0
            for i, bit in enumerate(bits):
                if x & (1 << bit):
                    mask |= 1 << i
            dp[mask] += 1
        for i in range(b):
            for mask in range(1 << b):
                if mask & (1 << i):
                    dp[mask] += dp[mask ^ (1 << i)]

        pow2 = [1] * (len(nums) + 1)
        for i in range(len(nums)):
            pow2[i + 1] = (pow2[i] * 2) % MOD

        full = (1 << b) - 1
        ans = 0
        for mask in range(1, full + 1):
            sign = 1 if bin(mask).count("1") & 1 else -1
            ans = (ans + sign * pow2[dp[full ^ mask]]) % MOD
        return ans
# @lc code=end
