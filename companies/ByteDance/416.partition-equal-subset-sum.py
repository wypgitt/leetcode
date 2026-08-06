#
# @lc app=leetcode id=416 lang=python3
#
# [416] Partition Equal Subset Sum
#
# https://leetcode.com/problems/partition-equal-subset-sum/description/
#
# algorithms
# Medium (49.84%)
# Likes:    14056
# Dislikes: 301
# Total Accepted:    1.6M
# Total Submissions: 3.2M
# Testcase Example:  "[1,5,11,5]"
#
# Given an integer array nums, return true if you can partition the array into
# two subsets such that the sum of the elements in both subsets is equal or
# false otherwise.
#
# Example 1:
#
# Input: nums = [1,5,11,5]
# Output: true
# Explanation: The array can be partitioned as [1, 5, 5] and [11].
#
# Example 2:
#
# Input: nums = [1,2,3,5]
# Output: false
# Explanation: The array cannot be partitioned into equal sum subsets.
#
# Constraints:
#
# 1 <= nums.length <= 200
#
# 1 <= nums[i] <= 100
#

# @lc code=start

from typing import List


class Solution:
    def canPartition(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        0/1 knapsack subset-sum: partition exists iff total is even and some
        subset sums to total/2. DP boolean array over achievable sums.

        Algorithm:
        - If sum odd: False. target=sum//2.
        - dp[0]=True; for each num, update dp from target down to num.

        Complexity: O(n*target) time, O(target) space.
        """
        total = sum(nums)
        if total % 2:
            return False
        target = total // 2
        dp = [False] * (target + 1)
        dp[0] = True
        for num in nums:
            for s in range(target, num - 1, -1):
                dp[s] = dp[s] or dp[s - num]
            if dp[target]:
                return True
        return dp[target]

    def canPartitionDFS(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: DFS/memo on (index, remaining target) after early even-sum check.

        Algorithm:
        - Sort descending for pruning; memoize dfs(i, remain).

        Complexity: O(n*target) time/space with memo.
        """
        total = sum(nums)
        if total % 2:
            return False
        target = total // 2
        nums = sorted(nums, reverse=True)
        if nums[0] > target:
            return False
        memo = {}

        def dfs(i: int, remain: int) -> bool:
            if remain == 0:
                return True
            if i == len(nums) or remain < 0:
                return False
            key = (i, remain)
            if key in memo:
                return memo[key]
            memo[key] = dfs(i + 1, remain - nums[i]) or dfs(i + 1, remain)
            return memo[key]

        return dfs(0, target)
# @lc code=end
