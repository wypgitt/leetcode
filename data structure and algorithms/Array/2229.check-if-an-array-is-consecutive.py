#
# @lc app=leetcode id=2229 lang=python3
#
# [2229] Check if an Array Is Consecutive
#
# https://leetcode.com/problems/check-if-an-array-is-consecutive/description/
#
# algorithms
# Easy (62.27%)
# Likes:    90
# Dislikes: 11
# Total Accepted:    8.1K
# Total Submissions: 13.1K
# Testcase Example:  "[1,3,4,2]"
#
#
# Given an integer array nums, return true if nums is consecutive,
# otherwise return false.
#
# An array is consecutive if it contains every number in the range [x, x +
# n - 1] (inclusive), where x is the minimum number in the array and n is
# the length of the array.
#
# Example 1:
#
# Input: nums = [1,3,4,2]
# Output: true
# Explanation:
# The minimum value is 1 and the length of nums is 4.
# All of the values in the range [x, x + n - 1] = [1, 1 + 4 - 1] = [1, 4]
# = (1, 2, 3, 4) occur in nums.
# Therefore, nums is consecutive.
#
# Example 2:
#
# Input: nums = [1,3]
# Output: false
# Explanation:
# The minimum value is 1 and the length of nums is 2.
# The value 2 in the range [x, x + n - 1] = [1, 1 + 2 - 1], = [1, 2] = (1,
# 2) does not occur in nums.
# Therefore, nums is not consecutive.
#
# Example 3:
#
# Input: nums = [3,5,4]
# Output: true
# Explanation:
# The minimum value is 3 and the length of nums is 3.
# All of the values in the range [x, x + n - 1] = [3, 3 + 3 - 1] = [3, 5]
# = (3, 4, 5) occur in nums.
# Therefore, nums is consecutive.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^5
#
# @lc code=start
from typing import List


class Solution:
    def isConsecutive(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Premium. nums is consecutive if its values form a contiguous range of
        len(nums) distinct integers (permutation of [x, x+n-1]).

        Algorithm:
        - max - min + 1 == n and all unique (set size == n).

        Complexity: O(n) time, O(n) space.
        """
        return max(nums) - min(nums) + 1 == len(nums) and len(set(nums)) == len(nums)

    def isConsecutive_sort(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: sort and check adjacent differences are 1.

        Algorithm:
        - Sort; verify a[i+1]-a[i]==1 for all i.

        Complexity: O(n log n) time, O(n) space.
        """
        a = sorted(nums)
        return all(a[i + 1] - a[i] == 1 for i in range(len(a) - 1))
# @lc code=end
