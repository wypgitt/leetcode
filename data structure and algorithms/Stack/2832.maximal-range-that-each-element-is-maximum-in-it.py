#
# @lc app=leetcode id=2832 lang=python3
#
# [2832] Maximal Range That Each Element Is Maximum in It
#
# https://leetcode.com/problems/maximal-range-that-each-element-is-maximum-in-it/description/
#
# algorithms
# Medium (75.35%)
# Likes:    80
# Dislikes: 8
# Total Accepted:    6.5K
# Total Submissions: 8.6K
# Testcase Example:  "[1,5,4,3,6]"
#
#
# You are given a 0-indexed array nums of distinct integers.
#
# Let us define a 0-indexed array ans of the same length as nums in the
# following way:
#
# ans[i] is the maximum length of a subarray nums[l..r], such that the
# maximum element in that subarray is equal to nums[i].
#
# Return the array ans.
#
# Note that a subarray is a contiguous part of the array.
#
# Example 1:
#
# Input: nums = [1,5,4,3,6]
# Output: [1,4,2,1,5]
# Explanation: For nums[0] the longest subarray in which 1 is the maximum
# is nums[0..0] so ans[0] = 1.
# For nums[1] the longest subarray in which 5 is the maximum is nums[0..3]
# so ans[1] = 4.
# For nums[2] the longest subarray in which 4 is the maximum is nums[2..3]
# so ans[2] = 2.
# For nums[3] the longest subarray in which 3 is the maximum is nums[3..3]
# so ans[3] = 1.
# For nums[4] the longest subarray in which 6 is the maximum is nums[0..4]
# so ans[4] = 5.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5]
# Output: [1,2,3,4,5]
# Explanation: For nums[i] the longest subarray in which it's the maximum
# is nums[0..i] so ans[i] = i + 1.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# All elements in nums are distinct.
#
# @lc code=start
from typing import List


class Solution:
    def maximumLengthOfRanges(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Premium: nums has distinct ints. For each i, return the max length of a
        contiguous subarray where nums[i] is the maximum.

        Algorithm:
        - Monotonic decreasing stack finds previous/next strictly greater in one
          pass (treat end as sentinel). Range length = right - left - 1.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        ans = [0] * n
        stack: List[int] = []
        for i in range(n + 1):
            while stack and (i == n or nums[stack[-1]] < nums[i]):
                idx = stack.pop()
                left = stack[-1] if stack else -1
                ans[idx] = i - left - 1
            stack.append(i)
        return ans
# @lc code=end
