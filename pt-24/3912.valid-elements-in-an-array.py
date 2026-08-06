#
# @lc app=leetcode id=3912 lang=python3
#
# [3912] Valid Elements in an Array
#
# https://leetcode.com/problems/valid-elements-in-an-array/description/
#
# algorithms
# Easy (57.38%)
# Likes:    32
# Dislikes: 1
# Total Accepted:    40K
# Total Submissions: 69.8K
# Testcase Example:  "[1,2,4,2,3,2]"
#
#
# You are given an integer array nums.
#
# An element nums[i] is considered valid if it satisfies at least one of
# the following conditions:
#
# It is strictly greater than every element to its left.
#
# It is strictly greater than every element to its right.
#
# The first and last elements are always valid.
#
# Return an array of all valid elements in the same order as they appear
# in nums.
#
# Example 1:
#
# Input: nums = [1,2,4,2,3,2]
#
# Output: [1,2,4,3,2]
#
# Explanation:
#
# nums[0] and nums[5] are always valid.
#
# nums[1] and nums[2] are strictly greater than every element to their
# left.
#
# nums[4] is strictly greater than every element to its right.
#
# Thus, the answer is [1, 2, 4, 3, 2].
#
# Example 2:
#
# Input: nums = [5,5,5,5]
#
# Output: [5,5]
#
# Explanation:
#
# The first and last elements are always valid.
#
# No other elements are strictly greater than all elements to their left
# or to their right.
#
# Thus, the answer is [5, 5].
#
# Example 3:
#
# Input: nums = [1]
#
# Output: [1]
#
# Explanation:
#
# Since there is only one element, it is always valid. Thus, the answer is
# [1].
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#

# @lc code=start
class Solution:
    def findValidElements(self, nums: list[int]) -> list[int]:
        """
        Interview explanation:
        Keep values that are strict prefix maxima, strict suffix maxima, or ends.

        Algorithm:
        - Mark left-to-right strict record highs and right-to-left strict highs.
        - Ends are always valid; emit nums[i] when marked.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        ok = [False] * n
        ok[0] = ok[-1] = True
        mx = nums[0]
        for i in range(1, n):
            if nums[i] > mx:
                ok[i] = True
                mx = nums[i]
        mx = nums[-1]
        for i in range(n - 2, -1, -1):
            if nums[i] > mx:
                ok[i] = True
                mx = nums[i]
        return [nums[i] for i in range(n) if ok[i]]
# @lc code=end
