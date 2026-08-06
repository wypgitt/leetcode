#
# @lc app=leetcode id=413 lang=python3
#
# [413] Arithmetic Slices
#
# https://leetcode.com/problems/arithmetic-slices/description/
#
# algorithms
# Medium (64.87%)
# Likes:    5675
# Dislikes: 308
# Total Accepted:    378K
# Total Submissions: 583K
# Testcase Example:  "[1,2,3,4]"
#
# An integer array is called arithmetic if it consists of at least three
# elements and if the difference between any two consecutive elements is the
# same.
#
# For example, [1,3,5,7,9], [7,7,7,7], and [3,-1,-5,-9] are arithmetic
# sequences.
#
# Given an integer array nums, return the number of arithmetic subarrays of
# nums.
#
# A subarray is a contiguous subsequence of the array.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
# Output: 3
# Explanation: We have 3 arithmetic slices in nums: [1, 2, 3], [2, 3, 4] and
# [1,2,3,4] itself.
#
# Example 2:
#
# Input: nums = [1]
# Output: 0
#
# Constraints:
#
# 1 <= nums.length <= 5000
#
# -1000 <= nums[i] <= 1000
#

# @lc code=start

from typing import List


class Solution:
    def numberOfArithmeticSlices(self, nums: List[int]) -> int:
        """
        Interview explanation:
        DP: let dp[i] = number of arithmetic slices ending at i. If
        nums[i]-nums[i-1]==nums[i-1]-nums[i-2], then dp[i]=dp[i-1]+1.
        Answer is sum of dp.

        Algorithm:
        - Walk i from 2..n-1; maintain cur streak count; accumulate total.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        if n < 3:
            return 0
        total = cur = 0
        for i in range(2, n):
            if nums[i] - nums[i - 1] == nums[i - 1] - nums[i - 2]:
                cur += 1
                total += cur
            else:
                cur = 0
        return total
# @lc code=end
