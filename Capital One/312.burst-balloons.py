#
# @lc app=leetcode id=312 lang=python3
#
# [312] Burst Balloons
#
# https://leetcode.com/problems/burst-balloons/description/
#
# algorithms
# Hard (64.1%)
# Likes:    9913
# Dislikes: 295
# Total Accepted:    474K
# Total Submissions: 739K
# Testcase Example:  "[3,1,5,8]"
#
# You are given n balloons, indexed from 0 to n - 1. Each balloon is painted
# with a number on it represented by an array nums. You are asked to burst all
# the balloons.
#
# If you burst the i^th balloon, you will get nums[i - 1] * nums[i] * nums[i +
# 1] coins. If i - 1 or i + 1 goes out of bounds of the array, then treat it as
# if there is a balloon with a 1 painted on it.
#
# Return the maximum coins you can collect by bursting the balloons wisely.
#
# Example 1:
#
# Input: nums = [3,1,5,8]
# Output: 167
# Explanation:
# nums = [3,1,5,8] --> [3,5,8] --> [3,8] --> [8] --> []
# coins = 3*1*5 + 3*5*8 + 1*3*8 + 1*8*1 = 167
#
# Example 2:
#
# Input: nums = [1,5]
# Output: 10
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 300
#
# 0 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def maxCoins(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Interval DP: pad with 1s. dp[l][r] = max coins bursting open balloons
        strictly inside (l, r). Last balloon burst in (l,r) is k; coins =
        vals[l]*vals[k]*vals[r] + dp[l][k] + dp[k][r].

        Algorithm:
        - vals = [1] + nums + [1]
        - For length from 2..n-1, for each l, r = l+length, try every k in (l,r).

        Complexity: O(n^3) time, O(n^2) space.
        """
        vals = [1] + nums + [1]
        n = len(vals)
        dp = [[0] * n for _ in range(n)]
        for length in range(2, n):
            for l in range(n - length):
                r = l + length
                best = 0
                for k in range(l + 1, r):
                    best = max(
                        best,
                        vals[l] * vals[k] * vals[r] + dp[l][k] + dp[k][r],
                    )
                dp[l][r] = best
        return dp[0][n - 1]
# @lc code=end

