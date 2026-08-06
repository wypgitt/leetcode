#
# @lc app=leetcode id=503 lang=python3
#
# [503] Next Greater Element II
#
# https://leetcode.com/problems/next-greater-element-ii/description/
#
# algorithms
# Medium (68.92%)
# Likes:    9360
# Dislikes: 247
# Total Accepted:    887K
# Total Submissions: 1.3M
# Testcase Example:  "[1,2,1]"
#
# Given a circular integer array nums (i.e., the next element of
# nums[nums.length - 1] is nums[0]), return the next greater number for every
# element in nums.
#
# The next greater number of a number x is the first greater number to its
# traversing-order next in the array, which means you could search circularly
# to find its next greater number. If it doesn't exist, return -1 for this
# number.
#
# Example 1:
#
# Input: nums = [1,2,1]
# Output: [2,-1,2]
# Explanation: The first 1's next greater number is 2;
# The number 2 can't find next greater number.
# The second 1's next greater number needs to search circularly, which is also
# 2.
#
# Example 2:
#
# Input: nums = [1,2,3,4,3]
# Output: [2,3,4,-1,4]
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def nextGreaterElements(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Circular next-greater: monotonic decreasing stack of indices; scan the
        array twice (mod n) so each element can see candidates wrapping around.

        Algorithm:
        - ans = [-1]*n; stack = []
        - For i in 0..2n-1: x = nums[i%n]
          while stack and nums[stack[-1]] < x: ans[stack.pop()] = x
          if i < n: stack.append(i)

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        ans = [-1] * n
        stack = []
        for i in range(2 * n):
            x = nums[i % n]
            while stack and nums[stack[-1]] < x:
                ans[stack.pop()] = x
            if i < n:
                stack.append(i)
        return ans
# @lc code=end
