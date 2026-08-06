#
# @lc app=leetcode id=26 lang=python3
#
# [26] Remove Duplicates from Sorted Array
#
# https://leetcode.com/problems/remove-duplicates-from-sorted-array/description/
#
# algorithms
# Easy (63.47%)
# Likes:    19542
# Dislikes: 20587
# Total Accepted:    8.3M
# Total Submissions: 13M
# Testcase Example:  "[1,1,2]"
#
# Given an integer array nums sorted in non-decreasing order, remove the
# duplicates in-place such that each unique element appears only once. The
# relative order of the elements should be kept the same.
#
# Consider the number of unique elements in nums to be k. After removing
# duplicates, return the number of unique elements k.
#
# The first k elements of nums should contain the unique numbers in sorted
# order. The remaining elements beyond index k - 1 can be ignored.
#
# Custom Judge:
#
# The judge will test your solution with the following code:
#
# int[] nums = [...]; // Input array
# int[] expectedNums = [...]; // The expected answer with correct length
#
# int k = removeDuplicates(nums); // Calls your implementation
#
# assert k == expectedNums.length;
# for (int i = 0; i < k; i++) {
# assert nums[i] == expectedNums[i];
# }
#
# If all assertions pass, then your solution will be accepted.
#
# Example 1:
#
# Input: nums = [1,1,2]
# Output: 2, nums = [1,2,_]
# Explanation: Your function should return k = 2, with the first two elements
# of nums being 1 and 2 respectively.
# It does not matter what you leave beyond the returned k (hence they are
# underscores).
#
# Example 2:
#
# Input: nums = [0,0,1,1,1,2,2,3,3,4]
# Output: 5, nums = [0,1,2,3,4,_,_,_,_,_]
# Explanation: Your function should return k = 5, with the first five elements
# of nums being 0, 1, 2, 3, and 4 respectively.
# It does not matter what you leave beyond the returned k (hence they are
# underscores).
#
# Constraints:
#
# 1 <= nums.length <= 3 * 10^4
#
# -100 <= nums[i] <= 100
#
# nums is sorted in non-decreasing order.
#

# @lc code=start
from typing import List


class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Array is sorted, so duplicates are adjacent. Compact unique values into
        the front of the array in-place and return the new length k.

        Algorithm:
        - `write` is the next index for a unique value; start at 1.
        - Scan with `read` from 1..n-1.
        - When nums[read] != nums[write - 1], write it at `write` and advance.
        - Return `write` as the count of unique elements.

        Complexity: O(n) time, O(1) space.
        """
        if not nums:
            return 0

        write = 1
        for read in range(1, len(nums)):
            if nums[read] != nums[write - 1]:
                nums[write] = nums[read]
                write += 1
        return write
# @lc code=end
