#
# @lc app=leetcode id=905 lang=python3
#
# [905] Sort Array By Parity
#
# https://leetcode.com/problems/sort-array-by-parity/description/
#
# algorithms
# Easy (76.61%)
# Likes:    5753
# Dislikes: 158
# Total Accepted:    1.1M
# Total Submissions: 1.4M
# Testcase Example:  "[3,1,2,4]"
#
# Given an integer array nums, move all the even integers at the beginning of
# the array followed by all the odd integers.
#
# Return any array that satisfies this condition.
#
# Example 1:
#
# Input: nums = [3,1,2,4]
# Output: [2,4,3,1]
# Explanation: The outputs [4,2,3,1], [2,4,1,3], and [4,2,1,3] would also be
# accepted.
#
# Example 2:
#
# Input: nums = [0]
# Output: [0]
#
# Constraints:
#
# 1 <= nums.length <= 5000
#
# 0 <= nums[i] <= 5000
#

# @lc code=start
from typing import List


class Solution:
    def sortArrayByParity(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Move all even numbers before odds (order among same parity free).
        Two pointers swap: left seeks odd, right seeks even.

        Algorithm (two pointers):
        - l,r=0,n-1. While l<r: if nums[l] even l++; elif nums[r] odd r--;
          else swap.

        Complexity: O(n) time, O(1) extra space.
        """
        l, r = 0, len(nums) - 1
        while l < r:
            if nums[l] % 2 == 0:
                l += 1
            elif nums[r] % 2 == 1:
                r -= 1
            else:
                nums[l], nums[r] = nums[r], nums[l]
                l += 1
                r -= 1
        return nums

    def sortArrayByParity_stable(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: partition into evens + odds lists (stable relative order).

        Algorithm:
        - return [x for x in nums if x%2==0] + [x for x in nums if x%2].

        Complexity: O(n) time/space.
        """
        return [x for x in nums if x % 2 == 0] + [x for x in nums if x % 2]
# @lc code=end

