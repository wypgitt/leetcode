#
# @lc app=leetcode id=1799 lang=python3
#
# [1799] Maximize Score After N Operations
#
# https://leetcode.com/problems/maximize-score-after-n-operations/description/
#
# algorithms
# Hard (57.9%)
# Likes:    1742
# Dislikes: 114
# Total Accepted:    71.6K
# Total Submissions: 124K
# Testcase Example:  "[1,2]"
#
# You are given nums, an array of positive integers of size 2 * n. You must
# perform n operations on this array.
#
# In the i^th operation (1-indexed), you will:
#
# Choose two elements, x and y.
#
# Receive a score of i * gcd(x, y).
#
# Remove x and y from nums.
#
# Return the maximum score you can receive after performing n operations.
#
# The function gcd(x, y) is the greatest common divisor of x and y.
#
# Example 1:
#
# Input: nums = [1,2]
# Output: 1
# Explanation: The optimal choice of operations is:
# (1 * gcd(1, 2)) = 1
#
# Example 2:
#
# Input: nums = [3,4,6,8]
# Output: 11
# Explanation: The optimal choice of operations is:
# (1 * gcd(3, 6)) + (2 * gcd(4, 8)) = 3 + 8 = 11
#
# Example 3:
#
# Input: nums = [1,2,3,4,5,6]
# Output: 14
# Explanation: The optimal choice of operations is:
# (1 * gcd(1, 5)) + (2 * gcd(2, 4)) + (3 * gcd(3, 6)) = 1 + 4 + 9 = 14
#
# Constraints:
#
# 1 <= n <= 7
#
# nums.length == 2 * n
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start
from typing import List
from functools import lru_cache
import math


class Solution:
    def maxScore(self, nums: List[int]) -> int:
        """
        Interview explanation:
        2n numbers; n operations: i-th op picks two unused, scores i * gcd.
        Bitmask DP over used indices: dp[mask] = max score with bits in mask used.

        Algorithm:
        - n2=len(nums); dfs(mask): op = popcount(mask)//2 + 1
        - Try all pairs i<j unused: score = op*gcd + dfs(mask|bit_i|bit_j)

        Complexity: O(2^{2n} * n^2) time, O(2^{2n}) space.
        """
        n2 = len(nums)

        @lru_cache(None)
        def dfs(mask: int) -> int:
            used = bin(mask).count("1")
            if used == n2:
                return 0
            op = used // 2 + 1
            best = 0
            for i in range(n2):
                if mask & (1 << i):
                    continue
                for j in range(i + 1, n2):
                    if mask & (1 << j):
                        continue
                    best = max(
                        best,
                        op * math.gcd(nums[i], nums[j])
                        + dfs(mask | (1 << i) | (1 << j)),
                    )
            return best

        return dfs(0)

    def maxScore_iter(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate iterative bitmask DP: for each mask with even popcount,
        try pairs to transition forward.

        Algorithm:
        - dp[0]=0; for mask: if popcount even: try add pair → update new mask.

        Complexity: O(2^{2n} * n^2).
        """
        n2 = len(nums)
        N = 1 << n2
        dp = [0] * N
        for mask in range(N):
            used = bin(mask).count("1")
            if used & 1:
                continue
            op = used // 2 + 1
            for i in range(n2):
                if mask & (1 << i):
                    continue
                for j in range(i + 1, n2):
                    if mask & (1 << j):
                        continue
                    nxt = mask | (1 << i) | (1 << j)
                    dp[nxt] = max(dp[nxt], dp[mask] + op * math.gcd(nums[i], nums[j]))
        return dp[N - 1]
# @lc code=end
