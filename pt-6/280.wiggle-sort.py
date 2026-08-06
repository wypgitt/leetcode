#
# @lc app=leetcode id=280 lang=python3
#
# [280] Wiggle Sort
#
# https://leetcode.com/problems/wiggle-sort/description/
#
# algorithms
# Medium (68.49%)
# Likes:    1248
# Dislikes: 103
# Total Accepted:    159.9K
# Total Submissions: 233.5K
# Testcase Example:  "[3,5,2,1,6,4]"
#
#
# Given an integer array nums, reorder it such that nums[0] <= nums[1] >=
# nums[2] <= nums[3]....
#
# You may assume the input array always has a valid answer.
#
# Example 1:
#
# Input: nums = [3,5,2,1,6,4]
# Output: [3,5,1,6,2,4]
# Explanation: [1,6,2,5,3,4] is also accepted.
#
# Example 2:
#
# Input: nums = [6,6,5,6,3,8]
# Output: [6,6,5,6,3,8]
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^4
#
# 0 <= nums[i] <= 10^4
#
# It is guaranteed that there will be an answer for the given input nums.
#
# Follow up: Could you solve the problem in O(n) time complexity?
#
# @lc code=start
from typing import List


class Solution:
    def wiggleSort(self, nums: List[int]) -> None:
        """
        Interview explanation:
        Rearrange so nums[0] <= nums[1] >= nums[2] <= nums[3] >= ...
        One pass: at odd indices enforce local peak; at even enforce local valley
        by swapping with neighbor when the inequality fails.

        Algorithm:
        - For i in 0..n-2:
          - If i odd and nums[i] < nums[i+1]: swap
          - If i even and nums[i] > nums[i+1]: swap

        Complexity: O(n) time, O(1) space. Modifies in place.
        """
        for i in range(len(nums) - 1):
            if (i % 2 == 0 and nums[i] > nums[i + 1]) or (
                i % 2 == 1 and nums[i] < nums[i + 1]
            ):
                nums[i], nums[i + 1] = nums[i + 1], nums[i]
# @lc code=end

