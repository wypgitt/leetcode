#
# @lc app=leetcode id=3423 lang=python3
#
# [3423] Maximum Difference Between Adjacent Elements in a Circular Array
#
# https://leetcode.com/problems/maximum-difference-between-adjacent-elements-in-a-circular-array/description/
#
# algorithms
# Easy (75.62%)
# Likes:    336
# Dislikes: 7
# Total Accepted:    169.6K
# Total Submissions: 224.2K
# Testcase Example:  "[1,2,4]"
#
#
# Given a circular array nums, find the maximum absolute difference
# between adjacent elements.
#
# Note: In a circular array, the first and last elements are adjacent.
#
# Example 1:
#
# Input: nums = [1,2,4]
#
# Output: 3
#
# Explanation:
#
# Because nums is circular, nums[0] and nums[2] are adjacent. They have
# the maximum absolute difference of |4 - 1| = 3.
#
# Example 2:
#
# Input: nums = [-5,-10,-5]
#
# Output: 5
#
# Explanation:
#
# The adjacent elements nums[0] and nums[1] have the maximum absolute
# difference of |-5 - (-10)| = 5.
#
# Constraints:
#
# 2 <= nums.length <= 100
#
# -100 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def maxAdjacentDistance(self, nums: List[int]) -> int:
        """
        Interview explanation:
        In a circular array every consecutive pair is adjacent, including the wrap
        from last to first. The answer is the maximum absolute adjacent difference.

        Algorithm:
        - Scan i over [0..n-1] and take max |nums[i] - nums[i-1]| (Python negative
          index wraps to the last element).

        Complexity: O(n) time, O(1) space.
        """
        return max(abs(nums[i] - nums[i - 1]) for i in range(len(nums)))
# @lc code=end
