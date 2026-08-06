#
# @lc app=leetcode id=3151 lang=python3
#
# [3151] Special Array I
#
# https://leetcode.com/problems/special-array-i/description/
#
# algorithms
# Easy (81.64%)
# Likes:    590
# Dislikes: 33
# Total Accepted:    267.2K
# Total Submissions: 327.3K
# Testcase Example:  "[1]"
#
#
# An array is considered special if the parity of every pair of adjacent
# elements is different. In other words, one element in each pair must be
# even, and the other must be odd.
#
# You are given an array of integers nums. Return true if nums is a
# special array, otherwise, return false.
#
# Example 1:
#
# Input: nums = [1]
#
# Output: true
#
# Explanation:
#
# There is only one element. So the answer is true.
#
# Example 2:
#
# Input: nums = [2,1,4]
#
# Output: true
#
# Explanation:
#
# There is only two pairs: (2,1) and (1,4), and both of them contain
# numbers with different parity. So the answer is true.
#
# Example 3:
#
# Input: nums = [4,3,1,6]
#
# Output: false
#
# Explanation:
#
# nums[1] and nums[2] are both odd. So the answer is false.
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
    def isArraySpecial(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Special means every adjacent pair has different parity.

        Algorithm:
        - Walk adjacent pairs; reject if (a % 2) == (b % 2).

        Complexity: O(n) time, O(1) space.
        """
        for i in range(len(nums) - 1):
            if (nums[i] & 1) == (nums[i + 1] & 1):
                return False
        return True

    def isArraySpecial_zip(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: zip consecutive pairs and check XOR of LSBs is 1.

        Algorithm:
        - all((a ^ b) & 1 for a, b in zip(nums, nums[1:])).

        Complexity: O(n) time, O(1) space.
        """
        return all((a ^ b) & 1 for a, b in zip(nums, nums[1:]))
# @lc code=end
