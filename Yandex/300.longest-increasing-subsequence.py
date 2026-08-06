#
# @lc app=leetcode id=300 lang=python3
#
# [300] Longest Increasing Subsequence
#
# https://leetcode.com/problems/longest-increasing-subsequence/description/
#
# algorithms
# Medium (59.79%)
# Likes:    22955
# Dislikes: 519
# Total Accepted:    2.7M
# Total Submissions: 4.6M
# Testcase Example:  "[10,9,2,5,3,7,101,18]"
#
# Given an integer array nums, return the length of the longest strictly
# increasing subsequence.
#
# Example 1:
#
# Input: nums = [10,9,2,5,3,7,101,18]
# Output: 4
# Explanation: The longest increasing subsequence is [2,3,7,101], therefore the
# length is 4.
#
# Example 2:
#
# Input: nums = [0,1,0,3,2,3]
# Output: 4
#
# Example 3:
#
# Input: nums = [7,7,7,7,7,7,7]
# Output: 1
#
# Constraints:
#
# 1 <= nums.length <= 2500
#
# -10^4 <= nums[i] <= 10^4
#
# Follow up: Can you come up with an algorithm that runs in O(n log(n)) time
# complexity?
#

# @lc code=start
from bisect import bisect_left
from typing import List


class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Patience sorting: maintain tails[i] = smallest tail of all increasing
        subsequences of length i+1. Binary search the insertion point for each
        num; replace or append. Length of tails is LIS length.

        Complexity: O(n log n) time, O(n) space.
        """
        tails: List[int] = []
        for x in nums:
            i = bisect_left(tails, x)
            if i == len(tails):
                tails.append(x)
            else:
                tails[i] = x
        return len(tails)

    def lengthOfLIS_DP(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate classic DP: dp[i] = LIS ending at i = 1 + max dp[j] for j < i
        with nums[j] < nums[i]. Answer is max(dp).

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(nums)
        dp = [1] * n
        for i in range(n):
            for j in range(i):
                if nums[j] < nums[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return max(dp) if dp else 0
# @lc code=end

