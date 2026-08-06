#
# @lc app=leetcode id=2529 lang=python3
#
# [2529] Maximum Count of Positive Integer and Negative Integer
#
# https://leetcode.com/problems/maximum-count-of-positive-integer-and-negative-integer/description/
#
# algorithms
# Easy (74.24%)
# Likes:    1609
# Dislikes: 92
# Total Accepted:    379K
# Total Submissions: 510.6K
# Testcase Example:  "[-2,-1,-1,1,2,3]"
#
# Given an array nums sorted in non-decreasing order, return the maximum between
# the number of positive integers and the number of negative integers.
#
#
# In other words, if the number of positive integers in nums is pos and the
# number of negative integers is neg, then return the maximum of pos and neg.
#
# Note that 0 is neither positive nor negative.
#
#
#
# Example 1:
#
# Input: nums = [-2,-1,-1,1,2,3]
# Output: 3
# Explanation: There are 3 positive integers and 3 negative integers. The
# maximum count among them is 3.
#
# Example 2:
#
# Input: nums = [-3,-2,-1,0,0,1,2]
# Output: 3
# Explanation: There are 2 positive integers and 3 negative integers. The
# maximum count among them is 3.
#
# Example 3:
#
# Input: nums = [5,20,66,1314]
# Output: 4
# Explanation: There are 4 positive integers and 0 negative integers. The
# maximum count among them is 4.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 2000
#
#
# -2000 <= nums[i] <= 2000
#
#
# nums is sorted in a non-decreasing order.
#
#
#
# Follow up: Can you solve the problem in O(log(n)) time complexity?
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def maximumCount(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sorted nums; return max(#negatives, #positives). Zeros count as neither.

        Algorithm:
        - Binary search: first index of 0 (end of negatives) and first index > 0
          (start of positives) via bisect.

        Complexity: O(log n) time, O(1) space.
        """
        neg = bisect.bisect_left(nums, 0)
        pos = len(nums) - bisect.bisect_right(nums, 0)
        return max(neg, pos)

    def maximumCount_linear(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same max(neg, pos) via a single left-to-right scan.

        Algorithm:
        - Count negatives and positives in one pass.

        Complexity: O(n) time, O(1) space.
        """
        neg = pos = 0
        for x in nums:
            if x < 0:
                neg += 1
            elif x > 0:
                pos += 1
        return max(neg, pos)
# @lc code=end
