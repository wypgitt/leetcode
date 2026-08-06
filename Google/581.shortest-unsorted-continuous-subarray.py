#
# @lc app=leetcode id=581 lang=python3
#
# [581] Shortest Unsorted Continuous Subarray
#
# https://leetcode.com/problems/shortest-unsorted-continuous-subarray/description/
#
# algorithms
# Medium (38.49%)
# Likes:    8081
# Dislikes: 278
# Total Accepted:    407K
# Total Submissions: 1.1M
# Testcase Example:  "[2,6,4,8,10,9,15]"
#
# Given an integer array nums, you need to find one continuous subarray such
# that if you only sort this subarray in non-decreasing order, then the whole
# array will be sorted in non-decreasing order.
#
# Return the shortest such subarray and output its length.
#
# Example 1:
#
# Input: nums = [2,6,4,8,10,9,15]
# Output: 5
# Explanation: You need to sort [6, 4, 8, 10, 9] in ascending order to make the
# whole array sorted in ascending order.
#
# Example 2:
#
# Input: nums = [1,2,3,4]
# Output: 0
#
# Example 3:
#
# Input: nums = [1]
# Output: 0
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -10^5 <= nums[i] <= 10^5
#
# Follow up: Can you solve it in O(n) time complexity?
#


# @lc code=start
from typing import List
class Solution:
    def findUnsortedSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        The shortest unsorted subarray is the segment that, once sorted, makes
        the whole array sorted. One pass from left finds the rightmost index
        that breaks non-decreasing order; from right finds the leftmost break.
        Track running max/min to locate those ends.

        Algorithm:
        - Left→right: maintain max_so_far; if nums[i] < max_so_far, end = i.
        - Right→left: maintain min_so_far; if nums[i] > min_so_far, start = i.
        - Length is end - start + 1, or 0 if already sorted.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        start, end = -1, -2
        max_so_far = float("-inf")
        min_so_far = float("inf")
        for i in range(n):
            max_so_far = max(max_so_far, nums[i])
            if nums[i] < max_so_far:
                end = i
            j = n - 1 - i
            min_so_far = min(min_so_far, nums[j])
            if nums[j] > min_so_far:
                start = j
        return end - start + 1

    def findUnsortedSubarraySort(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Compare nums to a sorted copy; the first and last mismatch indices
        bound the unsorted window. Simpler to explain; uses extra space.

        Algorithm:
        - sorted_nums = sorted(nums).
        - Find leftmost/rightmost i where nums[i] != sorted_nums[i].

        Complexity: O(n log n) time, O(n) space.
        """
        sorted_nums = sorted(nums)
        start, end = len(nums), 0
        for i, (a, b) in enumerate(zip(nums, sorted_nums)):
            if a != b:
                start = min(start, i)
                end = max(end, i)
        return end - start + 1 if end >= start else 0
# @lc code=end

