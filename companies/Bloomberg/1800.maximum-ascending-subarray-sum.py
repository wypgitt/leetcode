#
# @lc app=leetcode id=1800 lang=python3
#
# [1800] Maximum Ascending Subarray Sum
#
# https://leetcode.com/problems/maximum-ascending-subarray-sum/description/
#
# algorithms
# Easy (66.28%)
# Likes:    1305
# Dislikes: 44
# Total Accepted:    256K
# Total Submissions: 386K
# Testcase Example:  "[10,20,30,5,10,50]"
#
# Given an array of positive integers nums, return the maximum possible sum of
# an strictly increasing subarray in nums.
#
# A subarray is defined as a contiguous sequence of numbers in an array.
#
# Example 1:
#
# Input: nums = [10,20,30,5,10,50]
# Output: 65
# Explanation: [5,10,50] is the ascending subarray with the maximum sum of 65.
#
# Example 2:
#
# Input: nums = [10,20,30,40,50]
# Output: 150
# Explanation: [10,20,30,40,50] is the ascending subarray with the maximum sum
# of 150.
#
# Example 3:
#
# Input: nums = [12,17,15,13,10,11,12]
# Output: 33
# Explanation: [10,11,12] is the ascending subarray with the maximum sum of 33.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def maxAscendingSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Maximum sum of a strictly ascending contiguous subarray. Scan once;
        extend current run while nums[i] > nums[i-1], else reset.

        Algorithm:
        - cur=ans=nums[0]; for i=1..: if ascending cur+=nums[i] else cur=nums[i]; ans=max.

        Complexity: O(n) time, O(1) space.
        """
        ans = cur = nums[0]
        for i in range(1, len(nums)):
            if nums[i] > nums[i - 1]:
                cur += nums[i]
            else:
                cur = nums[i]
            ans = max(ans, cur)
        return ans

    def maxAscendingSum_segments(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: explicitly find each ascending segment and take max segment sum.

        Algorithm:
        - i=0; while i<n: grow j while strictly ascending; max sum(nums[i:j]); i=j.

        Complexity: O(n).
        """
        n = len(nums)
        ans = 0
        i = 0
        while i < n:
            j = i + 1
            s = nums[i]
            while j < n and nums[j] > nums[j - 1]:
                s += nums[j]
                j += 1
            ans = max(ans, s)
            i = j
        return ans
# @lc code=end
