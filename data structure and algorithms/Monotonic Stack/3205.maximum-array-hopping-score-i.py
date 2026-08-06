#
# @lc app=leetcode id=3205 lang=python3
#
# [3205] Maximum Array Hopping Score I
#
# https://leetcode.com/problems/maximum-array-hopping-score-i/description/
#
# algorithms
# Medium (77.10%)
# Likes:    28
# Dislikes: 1
# Total Accepted:    2.8K
# Total Submissions: 3.6K
# Testcase Example:  "[1,5,8]"
#
#
# Given an array nums, you have to get the maximum score starting from
# index 0 and hopping until you reach the last element of the array.
#
# In each hop, you can jump from index i to an index j > i, and you get a
# score of (j - i) * nums[j].
#
# Return the maximum score you can get.
#
# Example 1:
#
# Input: nums = [1,5,8]
#
# Output: 16
#
# Explanation:
#
# There are two possible ways to reach the last element:
#
# 0 -> 1 -> 2 with a score of (1 - 0) * 5 + (2 - 1) * 8 = 13.
#
# 0 -> 2 with a score of (2 - 0) * 8 = 16.
#
# Example 2:
#
# Input: nums = [4,5,2,8,9,1,3]
#
# Output: 42
#
# Explanation:
#
# We can do the hopping 0 -> 4 -> 6 with a score of (4 - 0) * 9 + (6 - 4)
# * 3 = 42.
#
# Constraints:
#
# 2 <= nums.length <= 10^3
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxScore(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Hop from 0 to n-1; hop i→j (j>i) scores (j-i)*nums[j]. Maximize total.
        Optimal cost equals the sum of suffix maxima over indices 1..n-1.

        Algorithm:
        - Scan right to left; maintain running max of nums[i..n-1].
        - Add that max once for each position i from n-1 down to 1.

        Complexity: O(n) time, O(1) space.
        """
        score = 0
        mx = 0
        for i in range(len(nums) - 1, 0, -1):
            mx = max(mx, nums[i])
            score += mx
        return score

    def maxScore_dp(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Classic DP: dp[i] = max score from i to the end.

        Algorithm:
        - dp[n-1] = 0; for i from n-2 downto 0,
          dp[i] = max over j>i of (j-i)*nums[j] + dp[j].

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(nums)
        dp = [0] * n
        for i in range(n - 2, -1, -1):
            best = 0
            for j in range(i + 1, n):
                best = max(best, (j - i) * nums[j] + dp[j])
            dp[i] = best
        return dp[0]
# @lc code=end
