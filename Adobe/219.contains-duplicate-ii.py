#
# @lc app=leetcode id=219 lang=python3
#
# [219] Contains Duplicate II
#
# https://leetcode.com/problems/contains-duplicate-ii/description/
#
# algorithms
# Easy (51.72%)
# Likes:    7656
# Dislikes: 3335
# Total Accepted:    1.9M
# Total Submissions: 3.7M
# Testcase Example:  "[1,2,3,1]"
#
# Given an integer array nums and an integer k, return true if there are two
# distinct indices i and j in the array such that nums[i] == nums[j] and abs(i
# - j) <= k.
#
# Example 1:
#
# Input: nums = [1,2,3,1], k = 3
# Output: true
#
# Example 2:
#
# Input: nums = [1,0,1,1], k = 1
# Output: true
#
# Example 3:
#
# Input: nums = [1,2,3,1,2,3], k = 2
# Output: false
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#
# 0 <= k <= 10^5
#

# @lc code=start
from typing import List, Set


class Solution:
    def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
        """
        Interview explanation:
        Maintain a sliding window of the last k indices' values. If the current
        value is already in the window, we found a duplicate within distance k.

        Algorithm:
        - Keep a set of values in nums[i-k .. i-1].
        - For each nums[i]: if in set return True; add it; if window > k, remove nums[i-k].

        Complexity: O(n) time, O(min(n, k)) space.
        """
        window: Set[int] = set()
        for i, x in enumerate(nums):
            if x in window:
                return True
            window.add(x)
            if len(window) > k:
                window.remove(nums[i - k])
        return False
# @lc code=end
