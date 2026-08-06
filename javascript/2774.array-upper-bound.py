#
# @lc app=leetcode id=2774 lang=python3
#
# [2774] Array Upper Bound
#
# https://leetcode.com/problems/array-upper-bound/description/
#
# algorithms
# Easy (82.46%)
# Likes:    23
# Dislikes: 2
# Total Accepted:    2.4K
# Total Submissions: 2.9K
# Testcase Example:  "[3,4,5]\n5"
#
#
# Write code that enhances all arrays such that you can call the
# upperBound() method on any array and it will return the last index of a
# given target number. nums is a sorted ascending array of numbers that
# may contain duplicates. If the target number is not found in the array,
# return -1.
#
# Example 1:
#
# Input: nums = [3,4,5], target = 5
# Output: 2
# Explanation: Last index of target value is 2
#
# Example 2:
#
# Input: nums = [1,4,5], target = 2
# Output: -1
# Explanation: Because there is no digit 2 in the array, return -1.
#
# Example 3:
#
# Input: nums = [3,4,6,6,6,6,7], target = 6
# Output: 5
# Explanation: Last index of target value is 5
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -10^4 <= nums[i], target <= 10^4
#
# nums is sorted in ascending order.
#
# Follow up: Can you write an algorithm with O(log n) runtime complexity?
#
# @lc code=start
from typing import List


class Solution:
    def upperBound(self, arr: List[int], target: int) -> int:
        """
        Interview explanation:
        JS premium: Array.prototype.upperBound(target) on a sorted array — last
        index of target, or -1 if absent.

        Algorithm:
        - Binary search for rightmost position > target; check arr[left-1].

        Complexity: O(log n) time, O(1) space.
        """
        left, right = 0, len(arr)
        while left < right:
            mid = (left + right) // 2
            if arr[mid] > target:
                right = mid
            else:
                left = mid + 1
        return left - 1 if left > 0 and arr[left - 1] == target else -1
# @lc code=end
