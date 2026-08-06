#
# @lc app=leetcode id=35 lang=python3
#
# [35] Search Insert Position
#
# https://leetcode.com/problems/search-insert-position/description/
#
# algorithms
# Easy (51.92%)
# Likes:    19048
# Dislikes: 906
# Total Accepted:    5.0M
# Total Submissions: 9.7M
# Testcase Example:  "[1,3,5,6]"
#
# Given a sorted array of distinct integers and a target value, return the
# index if the target is found. If not, return the index where it would be if
# it were inserted in order.
#
# You must write an algorithm with O(log n) runtime complexity.
#
# Example 1:
#
# Input: nums = [1,3,5,6], target = 5
# Output: 2
#
# Example 2:
#
# Input: nums = [1,3,5,6], target = 2
# Output: 1
#
# Example 3:
#
# Input: nums = [1,3,5,6], target = 7
# Output: 4
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -10^4 <= nums[i] <= 10^4
#
# nums contains distinct values sorted in ascending order.
#
# -10^4 <= target <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Sorted distinct array + O(log n) requirement => binary search for the
        lower bound: first index where nums[i] >= target (insertion point if
        missing).

        Algorithm:
        - Maintain window [lo, hi) with hi = len(nums).
        - While lo < hi, mid = (lo + hi) // 2.
        - If nums[mid] < target, search right half (lo = mid + 1).
          Else search left half including mid (hi = mid).
        - Return lo.

        Complexity: O(log n) time, O(1) space.
        """
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < target:
                lo = mid + 1
            else:
                hi = mid
        return lo
# @lc code=end
