#
# @lc app=leetcode id=377 lang=python3
#
# [377] Combination Sum IV
#
# https://leetcode.com/problems/combination-sum-iv/description/
#
# algorithms
# Medium (55.25%)
# Likes:    7825
# Dislikes: 704
# Total Accepted:    621K
# Total Submissions: 1.1M
# Testcase Example:  "[1,2,3]"
#
# Given an array of distinct integers nums and a target integer target, return
# the number of possible combinations that add up to target.
#
# The test cases are generated so that the answer can fit in a 32-bit integer.
#
# Example 1:
#
# Input: nums = [1,2,3], target = 4
# Output: 7
# Explanation:
# The possible combination ways are:
# (1, 1, 1, 1)
# (1, 1, 2)
# (1, 2, 1)
# (1, 3)
# (2, 1, 1)
# (2, 2)
# (3, 1)
# Note that different sequences are counted as different combinations.
#
# Example 2:
#
# Input: nums = [9], target = 3
# Output: 0
#
# Constraints:
#
# 1 <= nums.length <= 200
#
# 1 <= nums[i] <= 1000
#
# All the elements of nums are unique.
#
# 1 <= target <= 1000
#
# Follow up: What if negative numbers are allowed in the given array? How does
# it change the problem? What limitation we need to add to the question to
# allow negative numbers?
#

# @lc code=start
from typing import List


class Solution:
    def combinationSum4(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Count ordered combinations (permutations of coin change) that sum to
        target — unbounded knapsack where order matters. dp[t] = ways to make t.

        Algorithm:
        - dp[0] = 1
        - For t from 1..target: for each num <= t: dp[t] += dp[t - num]
        - Outer loop is amount (order matters); inner is coins.

        Complexity: O(target * len(nums)) time, O(target) space.
        """
        dp = [0] * (target + 1)
        dp[0] = 1
        for t in range(1, target + 1):
            for num in nums:
                if num <= t:
                    dp[t] += dp[t - num]
        return dp[target]
# @lc code=end
