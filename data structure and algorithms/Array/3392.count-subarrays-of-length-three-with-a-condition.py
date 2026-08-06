#
# @lc app=leetcode id=3392 lang=python3
#
# [3392] Count Subarrays of Length Three With a Condition
#
# https://leetcode.com/problems/count-subarrays-of-length-three-with-a-condition/description/
#
# algorithms
# Easy (61.36%)
# Likes:    305
# Dislikes: 31
# Total Accepted:    153.7K
# Total Submissions: 250.4K
# Testcase Example:  "[1,2,1,4,1]"
#
#
# Given an integer array nums, return the number of subarrays of length 3
# such that the sum of the first and third numbers equals exactly half of
# the second number.
#
# Example 1:
#
# Input: nums = [1,2,1,4,1]
#
# Output: 1
#
# Explanation:
#
# Only the subarray [1,4,1] contains exactly 3 elements where the sum of
# the first and third numbers equals half the middle number.
#
# Example 2:
#
# Input: nums = [1,1,1]
#
# Output: 0
#
# Explanation:
#
# [1,1,1] is the only subarray of length 3. However, its first and third
# numbers do not add to half the middle number.
#
# Constraints:
#
# 3 <= nums.length <= 100
#
# -100 <= nums[i] <= 100
#

# @lc code=start

from typing import List


class Solution:
    def countSubarrays(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count windows of length 3 where first+third equals half the middle, i.e.
        2*(nums[i]+nums[i+2]) == nums[i+1].

        Algorithm:
        - Slide i over [0..n-3] and test the doubled-sum identity (avoids floats).

        Complexity: O(n) time, O(1) space.
        """
        return sum(
            1
            for i in range(len(nums) - 2)
            if 2 * (nums[i] + nums[i + 2]) == nums[i + 1]
        )
# @lc code=end
