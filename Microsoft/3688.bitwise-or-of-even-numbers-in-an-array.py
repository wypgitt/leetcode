#
# @lc app=leetcode id=3688 lang=python3
#
# [3688] Bitwise OR of Even Numbers in an Array
#
# https://leetcode.com/problems/bitwise-or-of-even-numbers-in-an-array/description/
#
# algorithms
# Easy (85.37%)
# Likes:    44
# Dislikes: 4
# Total Accepted:    77.2K
# Total Submissions: 90.5K
# Testcase Example:  "[1,2,3,4,5,6]"
#
#
# You are given an integer array nums.
#
# Return the bitwise OR of all even numbers in the array.
#
# If there are no even numbers in nums, return 0.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5,6]
#
# Output: 6
#
# Explanation:
#
# The even numbers are 2, 4, and 6. Their bitwise OR equals 6.
#
# Example 2:
#
# Input: nums = [7,9,11]
#
# Output: 0
#
# Explanation:
#
# There are no even numbers, so the result is 0.
#
# Example 3:
#
# Input: nums = [1,8,16]
#
# Output: 24
#
# Explanation:
#
# The even numbers are 8 and 16. Their bitwise OR equals 24.
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
    def evenNumberBitwiseORs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        OR all even values; identity for empty OR is 0.

        Algorithm:
        - Fold bitwise OR over nums[i] where nums[i] is even.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        for x in nums:
            if x % 2 == 0:
                ans |= x
        return ans
# @lc code=end
