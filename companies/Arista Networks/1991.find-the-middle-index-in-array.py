#
# @lc app=leetcode id=1991 lang=python3
#
# [1991] Find the Middle Index in Array
#
# https://leetcode.com/problems/find-the-middle-index-in-array/description/
#
# algorithms
# Easy (70.22%)
# Likes:    1609
# Dislikes: 80
# Total Accepted:    184K
# Total Submissions: 262K
# Testcase Example:  "[2,3,-1,8,4]"
#
# Given a 0-indexed integer array nums, find the leftmost middleIndex (i.e.,
# the smallest amongst all the possible ones).
#
# A middleIndex is an index where nums[0] + nums[1] + ... + nums[middleIndex-1]
# == nums[middleIndex+1] + nums[middleIndex+2] + ... + nums[nums.length-1].
#
# If middleIndex == 0, the left side sum is considered to be 0. Similarly, if
# middleIndex == nums.length - 1, the right side sum is considered to be 0.
#
# Return the leftmost middleIndex that satisfies the condition, or -1 if there
# is no such index.
#
# Example 1:
#
# Input: nums = [2,3,-1,8,4]
# Output: 3
# Explanation: The sum of the numbers before index 3 is: 2 + 3 + -1 = 4
# The sum of the numbers after index 3 is: 4 = 4
#
# Example 2:
#
# Input: nums = [1,-1,4]
# Output: 2
# Explanation: The sum of the numbers before index 2 is: 1 + -1 = 0
# The sum of the numbers after index 2 is: 0
#
# Example 3:
#
# Input: nums = [2,5]
# Output: -1
# Explanation: There is no valid middleIndex.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# -1000 <= nums[i] <= 1000
#
# Note: This question is the same as 724:
# https://leetcode.com/problems/find-pivot-index/
#

# @lc code=start
from typing import List


class Solution:
    def findMiddleIndex(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Middle index: left sum == right sum (pivot index). Track left while
        subtracting from total.

        Algorithm:
        - total=sum; left=0; for i: if left==total-left-nums[i] return i; left+=nums[i].

        Complexity: O(n) time, O(1) space.
        """
        total = sum(nums)
        left = 0
        for i, x in enumerate(nums):
            if left == total - left - x:
                return i
            left += x
        return -1

    def findMiddleIndex_prefix(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate prefix-sum array; check pref[i]==total-pref[i+1].

        Algorithm:
        - Build prefix; scan for equality.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i] + x
        total = pref[n]
        for i in range(n):
            if pref[i] == total - pref[i + 1]:
                return i
        return -1
# @lc code=end

