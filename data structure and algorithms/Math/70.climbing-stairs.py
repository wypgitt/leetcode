#
# @lc app=leetcode id=70 lang=python3
#
# [70] Climbing Stairs
#
# https://leetcode.com/problems/climbing-stairs/description/
#
# algorithms
# Easy (54.26%)
# Likes:    24764
# Dislikes: 1053
# Total Accepted:    5.4M
# Total Submissions: 9.9M
# Testcase Example:  "2"
#
# You are climbing a staircase. It takes n steps to reach the top.
#
# Each time you can either climb 1 or 2 steps. In how many distinct ways can
# you climb to the top?
#
# Example 1:
#
# Input: n = 2
# Output: 2
# Explanation: There are two ways to climb to the top.
# 1. 1 step + 1 step
# 2. 2 steps
#
# Example 2:
#
# Input: n = 3
# Output: 3
# Explanation: There are three ways to climb to the top.
# 1. 1 step + 1 step + 1 step
# 2. 1 step + 2 steps
# 3. 2 steps + 1 step
#
# Constraints:
#
# 1 <= n <= 45
#

# @lc code=start
from functools import lru_cache


class Solution:
    def climbStairs(self, n: int) -> int:
        """
        Interview explanation:
        Ways to reach step n = ways(n-1) + ways(n-2) (last step is 1 or 2).
        This is the Fibonacci recurrence; keep only the previous two answers.

        Algorithm:
        - Base: 1 way for 1 step, 2 ways for 2 steps.
        - Iterate i from 3..n keeping only the previous two answers.
        - Return the nth value.

        Complexity: O(n) time, O(1) space.
        """
        if n <= 2:
            return n

        prev2, prev1 = 1, 2
        for _ in range(3, n + 1):
            prev2, prev1 = prev1, prev1 + prev2
        return prev1

    def climbStairsMemo(self, n: int) -> int:
        """
        Interview explanation:
        Top-down recursion for the same Fibonacci recurrence, with a cache so
        each subproblem ways(k) is computed once.

        Algorithm:
        - Define dfs(k): ways to climb k steps.
        - Base: k <= 2 returns k.
        - Otherwise return dfs(k - 1) + dfs(k - 2), memoized via lru_cache.

        Complexity: O(n) time, O(n) space.
        """
        @lru_cache(None)
        def dfs(k: int) -> int:
            if k <= 2:
                return k
            return dfs(k - 1) + dfs(k - 2)

        return dfs(n)
# @lc code=end
