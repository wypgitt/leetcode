#
# @lc app=leetcode id=704 lang=python3
#
# [704] Binary Search
#
# https://leetcode.com/problems/binary-search/description/
#
# algorithms
# Easy (61.27%)
# Likes:    13666
# Dislikes: 307
# Total Accepted:    4.2M
# Total Submissions: 6.8M
# Testcase Example:  "[-1,0,3,5,9,12]"
#
# Given an array of integers nums which is sorted in ascending order, and an
# integer target, write a function to search target in nums. If target exists,
# then return its index. Otherwise, return -1.
#
# You must write an algorithm with O(log n) runtime complexity.
#
# Example 1:
#
# Input: nums = [-1,0,3,5,9,12], target = 9
# Output: 4
# Explanation: 9 exists in nums and its index is 4
#
# Example 2:
#
# Input: nums = [-1,0,3,5,9,12], target = 2
# Output: -1
# Explanation: 2 does not exist in nums so return -1
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -10^4 < nums[i], target < 10^4
#
# All the integers in nums are unique.
#
# nums is sorted in ascending order.
#

# @lc code=start
from typing import List


class Solution:
    def search(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Classic binary search on a sorted ascending array: shrink [lo, hi] until
        the mid equals target or the window empties.

        Algorithm:
        - While lo <= hi: mid = (lo+hi)//2; compare nums[mid] with target.

        Complexity: O(log n) time, O(1) space.
        """
        lo, hi = 0, len(nums) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if nums[mid] == target:
                return mid
            if nums[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1
# @lc code=end
