#
# @lc app=leetcode id=2057 lang=python3
#
# [2057] Smallest Index With Equal Value
#
# https://leetcode.com/problems/smallest-index-with-equal-value/description/
#
# algorithms
# Easy (73.78%)
# Likes:    464
# Dislikes: 145
# Total Accepted:    92.2K
# Total Submissions: 124.9K
# Testcase Example:  "[0,1,2]"
#
# Given a 0-indexed integer array nums, return the smallest index i of nums such
# that i mod 10 == nums[i], or -1 if such index does not exist.
#
# x mod y denotes the remainder when x is divided by y.
#
#
#
# Example 1:
#
# Input: nums = [0,1,2]
# Output: 0
# Explanation:
# i=0: 0 mod 10 = 0 == nums[0].
# i=1: 1 mod 10 = 1 == nums[1].
# i=2: 2 mod 10 = 2 == nums[2].
# All indices have i mod 10 == nums[i], so we return the smallest index 0.
#
# Example 2:
#
# Input: nums = [4,3,2,1]
# Output: 2
# Explanation:
# i=0: 0 mod 10 = 0 != nums[0].
# i=1: 1 mod 10 = 1 != nums[1].
# i=2: 2 mod 10 = 2 == nums[2].
# i=3: 3 mod 10 = 3 != nums[3].
# 2 is the only index which has i mod 10 == nums[i].
#
# Example 3:
#
# Input: nums = [1,2,3,4,5,6,7,8,9,0]
# Output: -1
# Explanation: No index satisfies i mod 10 == nums[i].
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 100
#
#
# 0 <= nums[i] <= 9
#

# @lc code=start
from typing import List


class Solution:
    def smallestEqual(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Find the smallest index i such that i % 10 == nums[i], else -1.

        Algorithm:
        - Linear scan checking the modular equality.

        Complexity: O(n) time, O(1) space.
        """
        for i, x in enumerate(nums):
            if i % 10 == x:
                return i
        return -1
# @lc code=end
