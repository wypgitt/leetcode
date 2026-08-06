#
# @lc app=leetcode id=494 lang=python3
#
# [494] Target Sum
#
# https://leetcode.com/problems/target-sum/description/
#
# algorithms
# Medium (52.66%)
# Likes:    12562
# Dislikes: 422
# Total Accepted:    1.2M
# Total Submissions: 2.2M
# Testcase Example:  "[1,1,1,1,1]"
#
# You are given an integer array nums and an integer target.
#
# You want to build an expression out of nums by adding one of the symbols '+'
# and '-' before each integer in nums and then concatenate all the integers.
#
# For example, if nums = [2, 1], you can add a '+' before 2 and a '-' before 1
# and concatenate them to build the expression "+2-1".
#
# Return the number of different expressions that you can build, which
# evaluates to target.
#
# Example 1:
#
# Input: nums = [1,1,1,1,1], target = 3
# Output: 5
# Explanation: There are 5 ways to assign symbols to make the sum of nums be
# target 3.
# -1 + 1 + 1 + 1 + 1 = 3
# +1 - 1 + 1 + 1 + 1 = 3
# +1 + 1 - 1 + 1 + 1 = 3
# +1 + 1 + 1 - 1 + 1 = 3
# +1 + 1 + 1 + 1 - 1 = 3
#
# Example 2:
#
# Input: nums = [1], target = 1
# Output: 1
#
# Constraints:
#
# 1 <= nums.length <= 20
#
# 0 <= nums[i] <= 1000
#
# 0 <= sum(nums[i]) <= 1000
#
# -1000 <= target <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def findTargetSumWays(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Assign +/- to each num to reach target. Let P = positives, N = negatives:
        P+N = sum, P-N = target → P = (sum+target)/2. Count subsets with sum P
        (0/1 knapsack DP).

        Algorithm:
        - total = sum(nums); if (total+target) odd or |target|>total: 0
        - need = (total+target)//2; dp[0]=1; for x in nums: backward update dp.

        Complexity: O(n * sum) time, O(sum) space.
        """
        total = sum(nums)
        if (total + target) % 2 or abs(target) > total:
            return 0
        need = (total + target) // 2
        dp = [0] * (need + 1)
        dp[0] = 1
        for x in nums:
            for s in range(need, x - 1, -1):
                dp[s] += dp[s - x]
        return dp[need]

    def findTargetSumWays_dfs(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Alternate: DFS/memo on (index, remaining) — at each index try + or -.

        Complexity: O(n * sum) with memo, O(n * sum) space.
        """
        from functools import lru_cache

        @lru_cache(None)
        def dfs(i: int, rem: int) -> int:
            if i == len(nums):
                return 1 if rem == 0 else 0
            return dfs(i + 1, rem - nums[i]) + dfs(i + 1, rem + nums[i])

        return dfs(0, target)
# @lc code=end
