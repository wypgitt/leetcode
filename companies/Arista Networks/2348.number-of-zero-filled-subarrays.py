#
# @lc app=leetcode id=2348 lang=python3
#
# [2348] Number of Zero-Filled Subarrays
#
# https://leetcode.com/problems/number-of-zero-filled-subarrays/description/
#
# algorithms
# Medium (70.05%)
# Likes:    2801
# Dislikes: 96
# Total Accepted:    315.3K
# Total Submissions: 450.1K
# Testcase Example:  "[1,3,0,0,2,0,0,4]"
#
# Given an integer array nums, return the number of subarrays filled with 0.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
#
#
# Example 1:
#
# Input: nums = [1,3,0,0,2,0,0,4]
# Output: 6
# Explanation:
# There are 4 occurrences of [0] as a subarray.
# There are 2 occurrences of [0,0] as a subarray.
# There is no occurrence of a subarray with a size more than 2 filled with 0.
# Therefore, we return 6.
#
# Example 2:
#
# Input: nums = [0,0,0,2,0,0]
# Output: 9
# Explanation:
# There are 5 occurrences of [0] as a subarray.
# There are 3 occurrences of [0,0] as a subarray.
# There is 1 occurrence of [0,0,0] as a subarray.
# There is no occurrence of a subarray with a size more than 3 filled with 0.
# Therefore, we return 9.
#
# Example 3:
#
# Input: nums = [2,10,2019]
# Output: 0
# Explanation: There is no subarray filled with 0. Therefore, we return 0.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def zeroFilledSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count subarrays filled with only zeros.

        Algorithm:
        - For each consecutive zero run of length L, add L*(L+1)/2.

        Complexity: O(n) time, O(1) space.
        """
        ans = run = 0
        for x in nums:
            if x == 0:
                run += 1
                ans += run
            else:
                run = 0
        return ans

    def zeroFilledSubarray_math(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Run-length combinatorics (same as primary).

        Algorithm:
        - Accumulate triangular numbers per zero streak.

        Complexity: O(n) time, O(1) space.
        """
        return self.zeroFilledSubarray(nums)
# @lc code=end
