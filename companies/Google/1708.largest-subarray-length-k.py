#
# @lc app=leetcode id=1708 lang=python3
#
# [1708] Largest Subarray Length K
#
# https://leetcode.com/problems/largest-subarray-length-k/description/
#
# algorithms
# Easy (65.97%)
# Likes:    110
# Dislikes: 116
# Total Accepted:    10.9K
# Total Submissions: 16.5K
# Testcase Example:  "[1,4,5,2,3]\n3"
#
#
# An array A is larger than some array B if for the first index i where
# A[i] != B[i], A[i] > B[i].
#
# For example, consider 0-indexing:
#
# [1,3,2,4] > [1,2,2,4], since at index 1, 3 > 2.
#
# [1,4,4,4] < [2,1,1,1], since at index 0, 1 < 2.
#
# A subarray is a contiguous subsequence of the array.
#
# Given an integer array nums of distinct integers, return the largest
# subarray of nums of length k.
#
# Example 1:
#
# Input: nums = [1,4,5,2,3], k = 3
# Output: [5,2,3]
# Explanation: The subarrays of size 3 are: [1,4,5], [4,5,2], and [5,2,3].
# Of these, [5,2,3] is the largest.
#
# Example 2:
#
# Input: nums = [1,4,5,2,3], k = 4
# Output: [4,5,2,3]
# Explanation: The subarrays of size 4 are: [1,4,5,2], and [4,5,2,3].
# Of these, [4,5,2,3] is the largest.
#
# Example 3:
#
# Input: nums = [1,4,5,2,3], k = 1
# Output: [5]
#
# Constraints:
#
# 1 <= k <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# All the integers of nums are unique.
#
# Follow up: What if the integers in nums are not distinct?
#
# @lc code=start
from typing import List


class Solution:
    def largestSubarray(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Premium. Among all contiguous subarrays of length k, return the
        lexicographically largest. Equivalent to choosing the maximum starting
        element among indices [0, n-k] (first differing position decides order).

        Algorithm:
        - Find index i in [0, n-k] with maximum nums[i] (leftmost if ties not needed
          for lex since equal prefixes continue — max first element is enough when
          we take the max over starts; for full lex, scan starts for max nums[i:i+k]).
        - Actually for lex-largest length-k window: find start with max nums[start:start+k].
          Since equal length, compare windows; optimal is argmax of nums[i] for i in
          [0,n-k] because later elements only matter on ties — take first max start,
          then if ties continue... simplest: track best start by comparing windows.

        Complexity: O(n*k) naive compare, or O(n) since lex order of fixed-length
        windows is decided by first position: max of nums[0..n-k] then that window.
        (If two starts have same nums[i], need next; but standard LC 1708: just max
        starting value works for the stated problem.)
        """
        n = len(nums)
        best = 0
        for i in range(1, n - k + 1):
            if nums[i] > nums[best]:
                best = i
        return nums[best:best + k]

    def largestSubarray_compare(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Alternate: explicitly compare each length-k window lexicographically.

        Algorithm:
        - best = 0; for i in 1..n-k: if nums[i:i+k] > nums[best:best+k]: best = i

        Complexity: O(n*k) time, O(k) space for answer.
        """
        n = len(nums)
        best = 0
        for i in range(1, n - k + 1):
            if nums[i:i + k] > nums[best:best + k]:
                best = i
        return nums[best:best + k]
# @lc code=end
