#
# @lc app=leetcode id=2996 lang=python3
#
# [2996] Smallest Missing Integer Greater Than Sequential Prefix Sum
#
# https://leetcode.com/problems/smallest-missing-integer-greater-than-sequential-prefix-sum/description/
#
# algorithms
# Easy (35.84%)
# Likes:    190
# Dislikes: 313
# Total Accepted:    54.1K
# Total Submissions: 151K
# Testcase Example:  "[1,2,3,2,5]"
#
#
# You are given a 0-indexed array of integers nums.
#
# A prefix nums[0..i] is sequential if, for all 1 <= j <= i, nums[j] =
# nums[j - 1] + 1. In particular, the prefix consisting only of nums[0] is
# sequential.
#
# Return the smallest integer x missing from nums such that x is greater
# than or equal to the sum of the longest sequential prefix.
#
# Example 1:
#
# Input: nums = [1,2,3,2,5]
# Output: 6
# Explanation: The longest sequential prefix of nums is [1,2,3] with a sum
# of 6. 6 is not in the array, therefore 6 is the smallest missing integer
# greater than or equal to the sum of the longest sequential prefix.
#
# Example 2:
#
# Input: nums = [3,4,5,1,12,14,13]
# Output: 15
# Explanation: The longest sequential prefix of nums is [3,4,5] with a sum
# of 12. 12, 13, and 14 belong to the array while 15 does not. Therefore
# 15 is the smallest missing integer greater than or equal to the sum of
# the longest sequential prefix.
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# 1 <= nums[i] <= 50
#

# @lc code=start

from typing import List


class Solution:
    def missingInteger(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Longest sequential prefix: nums[0], nums[0]+1, ... consecutive +1.
        Let s = its sum; return smallest integer >= s missing from nums.

        Algorithm:
        - Walk prefix while consecutive; sum; put nums in a set; increment
          until missing.

        Complexity: O(n) time, O(n) space.
        """
        s = nums[0]
        i = 1
        while i < len(nums) and nums[i] == nums[i - 1] + 1:
            s += nums[i]
            i += 1
        present = set(nums)
        while s in present:
            s += 1
        return s
# @lc code=end
