#
# @lc app=leetcode id=813 lang=python3
#
# [813] Largest Sum of Averages
#
# https://leetcode.com/problems/largest-sum-of-averages/description/
#
# algorithms
# Medium (55.32%)
# Likes:    2221
# Dislikes: 105
# Total Accepted:    69.7K
# Total Submissions: 126K
# Testcase Example:  "[9,1,2,3,9]"
#
# You are given an integer array nums and an integer k. You can partition the
# array into at most k non-empty adjacent subarrays. The score of a partition
# is the sum of the averages of each subarray.
#
# Note that the partition must use every integer in nums, and that the score is
# not necessarily an integer.
#
# Return the maximum score you can achieve of all the possible partitions.
# Answers within 10^-6 of the actual answer will be accepted.
#
# Example 1:
#
# Input: nums = [9,1,2,3,9], k = 3
# Output: 20.00000
# Explanation:
# The best choice is to partition nums into [9], [1, 2, 3], [9]. The answer is
# 9 + (1 + 2 + 3) / 3 + 9 = 20.
# We could have also partitioned nums into [9, 1], [2], [3, 9], for example.
# That partition would lead to a score of 5 + 2 + 6 = 13, which is worse.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5,6,7], k = 4
# Output: 20.50000
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 10^4
#
# 1 <= k <= nums.length
#

# @lc code=start

from typing import List
from functools import lru_cache


class Solution:
    def largestSumOfAverages(self, nums: List[int], k: int) -> float:
        """
        Interview explanation:
        Partition into at most k contiguous groups; maximize sum of group
        averages. DP: dp[i][g] = best using first i elements with g groups.

        Algorithm (bottom-up DP):
        - prefix sums for O(1) range averages.
        - dp[i][1] = avg(0..i-1); dp[i][g] = max over j < i of dp[j][g-1]+avg(j..i-1).

        Complexity: O(n^2 * k) time, O(n*k) space.
        """
        n = len(nums)
        pref = [0.0] * (n + 1)
        for i, v in enumerate(nums):
            pref[i + 1] = pref[i] + v

        def avg(l: int, r: int) -> float:
            return (pref[r] - pref[l]) / (r - l)

        dp = [[0.0] * (k + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            dp[i][1] = avg(0, i)
        for g in range(2, k + 1):
            for i in range(g, n + 1):
                best = 0.0
                for j in range(g - 1, i):
                    best = max(best, dp[j][g - 1] + avg(j, i))
                dp[i][g] = best
        return dp[n][k]

    def largestSumOfAverages_memo(self, nums: List[int], k: int) -> float:
        """
        Interview explanation:
        Top-down memo: dfs(i, groups_left) = best from index i with remaining
        groups. Try every end of the next group.

        Algorithm:
        - prefix averages; recurse with memo.

        Complexity: O(n^2 * k) time, O(n*k) space.
        """
        n = len(nums)
        pref = [0.0] * (n + 1)
        for i, v in enumerate(nums):
            pref[i + 1] = pref[i] + v

        @lru_cache(None)
        def dfs(i: int, g: int) -> float:
            if g == 1:
                return (pref[n] - pref[i]) / (n - i)
            best = 0.0
            for j in range(i + 1, n - g + 2):
                best = max(best, (pref[j] - pref[i]) / (j - i) + dfs(j, g - 1))
            return best

        return dfs(0, k)
# @lc code=end
