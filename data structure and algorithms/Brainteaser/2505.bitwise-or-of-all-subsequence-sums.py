#
# @lc app=leetcode id=2505 lang=python3
#
# [2505] Bitwise OR of All Subsequence Sums
#
# https://leetcode.com/problems/bitwise-or-of-all-subsequence-sums/description/
#
# algorithms
# Medium (63.94%)
# Likes:    56
# Dislikes: 17
# Total Accepted:    4.5K
# Total Submissions: 7.1K
# Testcase Example:  "[2,1,0,3]"
#
#
# Given an integer array nums, return the value of the bitwise OR of the
# sum of all possible subsequences in the array.
#
# A subsequence is a sequence that can be derived from another sequence by
# removing zero or more elements without changing the order of the
# remaining elements.
#
# Example 1:
#
# Input: nums = [2,1,0,3]
# Output: 7
# Explanation: All possible subsequence sums that we can have are: 0, 1,
# 2, 3, 4, 5, 6.
# And we have 0 OR 1 OR 2 OR 3 OR 4 OR 5 OR 6 = 7, so we return 7.
#
# Example 2:
#
# Input: nums = [0,0,0]
# Output: 0
# Explanation: 0 is the only possible subsequence sum we can have, so we
# return 0.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^9
#
# @lc code=start
from typing import List


class Solution:
    def subsequenceSumOr(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Return the bitwise OR of sums of all non-empty subsequences of nums.

        Algorithm:
        - Accumulate prefix sum; ans |= x | prefix for each x. Prefix sums plus
          each element cover every bit that any subsequence sum can set (carries
          fill contiguous lower ranges).

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        prefix = 0
        for x in nums:
            prefix += x
            ans |= x | prefix
        return ans

    def subsequenceSumOr_bit(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Bit-count / carry view of the same OR: every bit that can appear in some
        subsequence sum via direct contribution or carry from lower bits.

        Algorithm:
        - Count how many numbers set each bit; if count[b] > 0 that bit appears in
          the OR; carry count[b]//2 into bit b+1 (pairs of contributions).

        Complexity: O(n * B) time, O(B) space (B ~ 64).
        """
        cnt = [0] * 64
        for x in nums:
            b = 0
            while x:
                if x & 1:
                    cnt[b] += 1
                x >>= 1
                b += 1
        ans = 0
        for b in range(63):
            if cnt[b]:
                ans |= 1 << b
            cnt[b + 1] += cnt[b] // 2
        return ans
# @lc code=end
