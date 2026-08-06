#
# @lc app=leetcode id=3702 lang=python3
#
# [3702] Longest Subsequence With Non-Zero Bitwise XOR
#
# https://leetcode.com/problems/longest-subsequence-with-non-zero-bitwise-xor/description/
#
# algorithms
# Medium (37.60%)
# Likes:    99
# Dislikes: 9
# Total Accepted:    33.2K
# Total Submissions: 88.2K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an integer array nums.
#
# Return the length of the longest subsequence in nums whose bitwise XOR
# is non-zero. If no such subsequence exists, return 0.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: 2
#
# Explanation:
#
# One longest subsequence is [2, 3]. The bitwise XOR is computed as 2 XOR
# 3 = 1, which is non-zero.
#
# Example 2:
#
# Input: nums = [2,3,4]
#
# Output: 3
#
# Explanation:
#
# The longest subsequence is [2, 3, 4]. The bitwise XOR is computed as 2
# XOR 3 XOR 4 = 5, which is non-zero.
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
    def longestSubsequence(self, nums: List[int]) -> int:
        """
        Interview explanation:
        XOR of a subsequence is zero iff the full XOR is zero and we keep every
        element (or the array is all zeros). Otherwise drop one non-zero value.

        Algorithm:
        - Compute total XOR and whether any non-zero exists.
        - If total XOR != 0: answer is n.
        - Else if some non-zero exists: answer is n - 1 (drop one non-zero).
        - Else: answer is 0.

        Complexity: O(n) time, O(1) space.
        """
        xor = 0
        has_nonzero = False
        for x in nums:
            xor ^= x
            if x:
                has_nonzero = True
        if xor:
            return len(nums)
        return len(nums) - 1 if has_nonzero else 0

    def longestSubsequence_scan(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate phrasing of the same XOR fact.

        Algorithm:
        - Same cases via reduce/any.

        Complexity: O(n) time, O(1) space.
        """
        from functools import reduce
        import operator

        n = len(nums)
        if reduce(operator.xor, nums, 0):
            return n
        return n - 1 if any(nums) else 0
# @lc code=end
