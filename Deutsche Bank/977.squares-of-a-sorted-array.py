#
# @lc app=leetcode id=977 lang=python3
#
# [977] Squares of a Sorted Array
#
# https://leetcode.com/problems/squares-of-a-sorted-array/description/
#
# algorithms
# Easy (74.03%)
# Likes:    10411
# Dislikes: 282
# Total Accepted:    2.8M
# Total Submissions: 3.8M
# Testcase Example:  "[-4,-1,0,3,10]"
#
# Given an integer array nums sorted in non-decreasing order, return an array
# of the squares of each number sorted in non-decreasing order.
#
# Example 1:
#
# Input: nums = [-4,-1,0,3,10]
# Output: [0,1,9,16,100]
# Explanation: After squaring, the array becomes [16,1,0,9,100].
# After sorting, it becomes [0,1,9,16,100].
#
# Example 2:
#
# Input: nums = [-7,-3,2,3,11]
# Output: [4,9,9,49,121]
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -10^4 <= nums[i] <= 10^4
#
# nums is sorted in non-decreasing order.
#
# Follow up: Squaring each element and sorting the new array is very trivial,
# could you find an O(n) solution using a different approach?
#

# @lc code=start
from typing import List


class Solution:
    def sortedSquares(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Array is sorted; largest absolute values are at the ends. Two pointers
        from both ends fill the result from largest square to smallest.

        Algorithm (two pointers):
        - lo=0, hi=n-1; write into res from the back.
        - Compare |nums[lo]| vs |nums[hi]| (via squares); place larger square
          at res[k], move that pointer, k--.

        Complexity: O(n) time, O(n) space for the answer.
        """
        n = len(nums)
        res = [0] * n
        lo, hi = 0, n - 1
        for k in range(n - 1, -1, -1):
            if abs(nums[lo]) > abs(nums[hi]):
                res[k] = nums[lo] * nums[lo]
                lo += 1
            else:
                res[k] = nums[hi] * nums[hi]
                hi -= 1
        return res

    def sortedSquares_sort(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate trivial: square every element then sort.

        Algorithm:
        - return sorted(x*x for x in nums).

        Complexity: O(n log n) time, O(n) space.
        """
        return sorted(x * x for x in nums)
# @lc code=end
