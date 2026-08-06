#
# @lc app=leetcode id=1480 lang=python3
#
# [1480] Running Sum of 1d Array
#
# https://leetcode.com/problems/running-sum-of-1d-array/description/
#
# algorithms
# Easy (87.05%)
# Likes:    8899
# Dislikes: 372
# Total Accepted:    2.5M
# Total Submissions: 2.9M
# Testcase Example:  "[1,2,3,4]"
#
# Given an array nums. We define a running sum of an array as runningSum[i] =
# sum(nums[0]…nums[i]).
#
# Return the running sum of nums.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
# Output: [1,3,6,10]
# Explanation: Running sum is obtained as follows: [1, 1+2, 1+2+3, 1+2+3+4].
#
# Example 2:
#
# Input: nums = [1,1,1,1,1]
# Output: [1,2,3,4,5]
# Explanation: Running sum is obtained as follows: [1, 1+1, 1+1+1, 1+1+1+1,
# 1+1+1+1+1].
#
# Example 3:
#
# Input: nums = [3,1,2,10,1]
# Output: [3,4,6,16,17]
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# -10^6 <= nums[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def runningSum(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Prefix sums: ans[i] = nums[0]+...+nums[i]. In-place or new array.

        Algorithm:
        - For i from 1..n-1: nums[i] += nums[i-1]; return nums.

        Complexity: O(n) time, O(1) extra space.
        """
        for i in range(1, len(nums)):
            nums[i] += nums[i - 1]
        return nums

    def runningSum_new(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: build a new prefix array without mutating input.

        Algorithm:
        - ans[0]=nums[0]; ans[i]=ans[i-1]+nums[i].

        Complexity: O(n) time/space.
        """
        ans = [nums[0]]
        for i in range(1, len(nums)):
            ans.append(ans[-1] + nums[i])
        return ans
# @lc code=end
