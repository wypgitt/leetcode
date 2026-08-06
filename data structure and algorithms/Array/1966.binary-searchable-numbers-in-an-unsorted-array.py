#
# @lc app=leetcode id=1966 lang=python3
#
# [1966] Binary Searchable Numbers in an Unsorted Array
#
# https://leetcode.com/problems/binary-searchable-numbers-in-an-unsorted-array/description/
#
# algorithms
# Medium (63.86%)
# Likes:    82
# Dislikes: 13
# Total Accepted:    4.3K
# Total Submissions: 6.7K
# Testcase Example:  "[7]"
#
#
# Consider a function that implements an algorithm similar to Binary
# Search. The function has two input parameters: sequence is a sequence of
# integers, and target is an integer value. The purpose of the function is
# to find if the target exists in the sequence.
#
# The pseudocode of the function is as follows:
#
# func(sequence, target)
#   while sequence is not empty
#     randomly choose an element from sequence as the pivot
#     if pivot = target, return true
#     else if pivot < target, remove pivot and all elements to its left
# from the sequence
#     else, remove pivot and all elements to its right from the sequence
#   end while
#   return false
#
# When the sequence is sorted, the function works correctly for all
# values. When the sequence is not sorted, the function does not work for
# all values, but may still work for some values.
#
# Given an integer array nums, representing the sequence, that contains
# unique numbers and may or may not be sorted, return the number of values
# that are guaranteed to be found using the function, for every possible
# pivot selection.
#
# Example 1:
#
# Input: nums = [7]
# Output: 1
# Explanation:
# Searching for value 7 is guaranteed to be found.
# Since the sequence has only one element, 7 will be chosen as the pivot.
# Because the pivot equals the target, the function will return true.
#
# Example 2:
#
# Input: nums = [-1,5,2]
# Output: 1
# Explanation:
# Searching for value -1 is guaranteed to be found.
# If -1 was chosen as the pivot, the function would return true.
# If 5 was chosen as the pivot, 5 and 2 would be removed. In the next
# loop, the sequence would have only -1 and the function would return
# true.
# If 2 was chosen as the pivot, 2 would be removed. In the next loop, the
# sequence would have -1 and 5. No matter which number was chosen as the
# next pivot, the function would find -1 and return true.
#
# Searching for value 5 is NOT guaranteed to be found.
# If 2 was chosen as the pivot, -1, 5 and 2 would be removed. The sequence
# would be empty and the function would return false.
#
# Searching for value 2 is NOT guaranteed to be found.
# If 5 was chosen as the pivot, 5 and 2 would be removed. In the next
# loop, the sequence would have only -1 and the function would return
# false.
#
# Because only -1 is guaranteed to be found, you should return 1.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^5 <= nums[i] <= 10^5
#
# All the values of nums are unique.
#
# Follow-up: If nums has duplicates, would you modify your algorithm? If
# so, how?
#
# @lc code=start
from typing import List


class Solution:
    def binarySearchableNumbers(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. nums[i] is always found by binary search iff it is strictly
        greater than every element to its left and strictly less than every
        element to its right.

        Algorithm:
        - Pref max left; suf min right; count i with left_max < nums[i] < right_min.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        left_max = [float("-inf")] * n
        for i in range(1, n):
            left_max[i] = max(left_max[i - 1], nums[i - 1])
        right_min = [float("inf")] * n
        for i in range(n - 2, -1, -1):
            right_min[i] = min(right_min[i + 1], nums[i + 1])
        return sum(1 for i in range(n) if left_max[i] < nums[i] < right_min[i])

    def binarySearchableNumbers_scan(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: candidates greater than all on the left, intersect with those
        smaller than all on the right.

        Algorithm:
        - Forward collect indices with nums[i] > running_max.
        - Backward set of indices with nums[i] < running_min; count intersection.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        left_ok = []
        mx = float("-inf")
        for i, x in enumerate(nums):
            if x > mx:
                left_ok.append(i)
                mx = x
        right_ok = set()
        mn = float("inf")
        for i in range(n - 1, -1, -1):
            if nums[i] < mn:
                right_ok.add(i)
                mn = nums[i]
        return sum(1 for i in left_ok if i in right_ok)
# @lc code=end


