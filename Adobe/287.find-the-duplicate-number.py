#
# @lc app=leetcode id=287 lang=python3
#
# [287] Find the Duplicate Number
#
# https://leetcode.com/problems/find-the-duplicate-number/description/
#
# algorithms
# Medium (64.72%)
# Likes:    25762
# Dislikes: 5898
# Total Accepted:    2.7M
# Total Submissions: 4.2M
# Testcase Example:  "[1,3,4,2,2]"
#
# Given an array of integers nums containing n + 1 integers where each integer
# is in the range [1, n] inclusive.
#
# There is only one repeated number in nums, return this repeated number.
#
# You must solve the problem without modifying the array nums and using only
# constant extra space.
#
# Example 1:
#
# Input: nums = [1,3,4,2,2]
# Output: 2
#
# Example 2:
#
# Input: nums = [3,1,3,4,2]
# Output: 3
#
# Example 3:
#
# Input: nums = [3,3,3,3,3]
# Output: 3
#
# Constraints:
#
# 1 <= n <= 10^5
#
# nums.length == n + 1
#
# 1 <= nums[i] <= n
#
# All the integers in nums appear only once except for precisely one integer
# which appears two or more times.
#
# Follow up:
#
# How can we prove that at least one duplicate number must exist in nums?
#
# Can you solve the problem in linear runtime complexity?
#

# @lc code=start
from typing import List


class Solution:
    def findDuplicate(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Values in [1,n] with length n+1 form a functional graph with a cycle
        (index → nums[index]). Floyd cycle detection finds the duplicate
        entrance in O(1) space without modifying the array.

        Algorithm (Floyd — primary):
        - Tortoise = nums[0], hare = nums[0]; advance 1 vs 2 until meet.
        - Reset tortoise to nums[0]; advance both by 1 until meet → duplicate.

        Complexity: O(n) time, O(1) space.
        """
        slow = fast = nums[0]
        while True:
            slow = nums[slow]
            fast = nums[nums[fast]]
            if slow == fast:
                break
        slow = nums[0]
        while slow != fast:
            slow = nums[slow]
            fast = nums[fast]
        return slow

    def findDuplicateBinarySearch(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: binary search on value. Count how many nums[i] <= mid; if
        count > mid, duplicate is in [1, mid], else in [mid+1, n].

        Complexity: O(n log n) time, O(1) space.
        """
        lo, hi = 1, len(nums) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            cnt = sum(x <= mid for x in nums)
            if cnt > mid:
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end

