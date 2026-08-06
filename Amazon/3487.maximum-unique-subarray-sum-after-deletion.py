#
# @lc app=leetcode id=3487 lang=python3
#
# [3487] Maximum Unique Subarray Sum After Deletion
#
# https://leetcode.com/problems/maximum-unique-subarray-sum-after-deletion/description/
#
# algorithms
# Easy (40.54%)
# Likes:    486
# Dislikes: 79
# Total Accepted:    159.6K
# Total Submissions: 393.5K
# Testcase Example:  "[1,2,3,4,5]"
#
#
# You are given an integer array nums.
#
# You are allowed to delete any number of elements from nums without
# making it empty. After performing the deletions, select a subarray of
# nums such that:
#
# All elements in the subarray are unique.
#
# The sum of the elements in the subarray is maximized.
#
# Return the maximum sum of such a subarray.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5]
#
# Output: 15
#
# Explanation:
#
# Select the entire array without deleting any element to obtain the
# maximum sum.
#
# Example 2:
#
# Input: nums = [1,1,0,1,1]
#
# Output: 1
#
# Explanation:
#
# Delete the element nums[0] == 1, nums[1] == 1, nums[2] == 0, and nums[3]
# == 1. Select the entire array [1] to obtain the maximum sum.
#
# Example 3:
#
# Input: nums = [1,2,-1,-2,1,0,-1]
#
# Output: 3
#
# Explanation:
#
# Delete the elements nums[2] == -1 and nums[3] == -2, and select the
# subarray [2, 1] from [1, 2, 1, 0, -1] to obtain the maximum sum.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# -100 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def maxSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Deletions can make any subset contiguous, so the problem reduces to
        the maximum sum of a set of distinct values. Prefer all unique
        positives; if none, take the largest (least negative / zero) value.

        Algorithm:
        - Sum unique positive numbers; else return max(nums).

        Complexity: O(n) time, O(n) space.
        """
        pos = {x for x in nums if x > 0}
        if pos:
            return sum(pos)
        return max(nums)

    def maxSum_scan(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate single-pass: track seen positives while computing the sum.

        Algorithm:
        - Seen set for unique positives; fall back to max element.

        Complexity: O(n) time, O(n) space.
        """
        seen = set()
        total = 0
        has_pos = False
        best = nums[0]
        for x in nums:
            best = max(best, x)
            if x > 0 and x not in seen:
                seen.add(x)
                total += x
                has_pos = True
        return total if has_pos else best
# @lc code=end
