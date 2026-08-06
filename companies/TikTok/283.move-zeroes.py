#
# @lc app=leetcode id=283 lang=python3
#
# [283] Move Zeroes
#
# https://leetcode.com/problems/move-zeroes/description/
#
# algorithms
# Easy (64.22%)
# Likes:    19734
# Dislikes: 612
# Total Accepted:    5.5M
# Total Submissions: 8.5M
# Testcase Example:  "[0,1,0,3,12]"
#
# Given an integer array nums, move all 0's to the end of it while maintaining
# the relative order of the non-zero elements.
#
# Note that you must do this in-place without making a copy of the array.
#
# Example 1:
#
# Input: nums = [0,1,0,3,12]
# Output: [1,3,12,0,0]
#
# Example 2:
#
# Input: nums = [0]
# Output: [0]
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -2^31 <= nums[i] <= 2^31 - 1
#
# Follow up: Could you minimize the total number of operations done?
#

# @lc code=start
from typing import List


class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        """
        Interview explanation:
        Move all zeros to the end while preserving relative order of non-zeros.
        Two pointers: write non-zeros forward, then fill the rest with zeros.

        Algorithm:
        - slow = next write index for a non-zero.
        - Scan fast; when nums[fast] != 0, write to nums[slow] and advance slow.
        - Fill nums[slow:] with 0.

        Complexity: O(n) time, O(1) space. In-place.
        """
        slow = 0
        for fast in range(len(nums)):
            if nums[fast] != 0:
                nums[slow] = nums[fast]
                slow += 1
        for i in range(slow, len(nums)):
            nums[i] = 0
# @lc code=end

