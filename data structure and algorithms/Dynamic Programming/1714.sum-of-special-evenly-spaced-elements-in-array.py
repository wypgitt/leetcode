#
# @lc app=leetcode id=1714 lang=python3
#
# [1714] Sum Of Special Evenly-Spaced Elements In Array
#
# https://leetcode.com/problems/sum-of-special-evenly-spaced-elements-in-array/description/
#
# algorithms
# Hard (49.66%)
# Likes:    34
# Dislikes: 27
# Total Accepted:    1.8K
# Total Submissions: 3.5K
# Testcase Example:  "[0,1,2,3,4,5,6,7]\n[[0,3],[5,1],[4,2]]"
#
#
# You are given a 0-indexed integer array nums consisting of n
# non-negative integers.
#
# You are also given an array queries, where queries[i] = [x_i, y_i]. The
# answer to the i^th query is the sum of all nums[j] where x_i <= j < n
# and (j - x_i) is divisible by y_i.
#
# Return an array answer where answer.length == queries.length and
# answer[i] is the answer to the i^th query modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [0,1,2,3,4,5,6,7], queries = [[0,3],[5,1],[4,2]]
# Output: [9,18,10]
# Explanation: The answers of the queries are as follows:
# 1) The j indices that satisfy this query are 0, 3, and 6. nums[0] +
# nums[3] + nums[6] = 9
# 2) The j indices that satisfy this query are 5, 6, and 7. nums[5] +
# nums[6] + nums[7] = 18
# 3) The j indices that satisfy this query are 4 and 6. nums[4] + nums[6]
# = 10
#
# Example 2:
#
# Input: nums = [100,200,101,201,102,202,103,203], queries = [[0,7]]
# Output: [303]
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 5 * 10^4
#
# 0 <= nums[i] <= 10^9
#
# 1 <= queries.length <= 1.5 * 10^5
#
# 0 <= x_i < n
#
# 1 <= y_i <= 5 * 10^4
#
# @lc code=start
from typing import List
import math


class Solution:
    def solve(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Premium. Each query [start, end] asks sum of nums[start] + nums[start+end]
        + nums[start+2*end] + ... (evenly spaced). Optimize with sqrt decomposition:
        large step → naive; small step → precomputed suffix sums per residue.

        Algorithm:
        - B = floor(sqrt(n)); for step y < B, precompute suf[y][i] = nums[i]+suf[y][i+y]
        - Answer query (x,y): if y>=B walk; else use suf[y][x]
        - MOD = 10^9+7

        Note: LeetCode signature is often `sumOfEvenlySpacedElements` / `solve`.
        Using solve as common premium stub; also provide sumEvenlySpaced alias.

        Complexity: O(n*sqrt(n) + q) time, O(n*sqrt(n)) space.
        """
        return self.sumEvenlySpaced(nums, queries)

    def sumEvenlySpaced(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Same sqrt-decomposition answer for evenly-spaced suffix sums.

        Algorithm:
        - See solve(); return answers mod 10^9+7.

        Complexity: O(n√n + q) time, O(n√n) space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        B = int(math.isqrt(n)) + 1
        # suf[y][i] for y in 1..B-1
        suf = [None] * B
        for y in range(1, B):
            s = [0] * n
            for i in range(n - 1, -1, -1):
                s[i] = nums[i] + (s[i + y] if i + y < n else 0)
            suf[y] = s
        ans = []
        for x, y in queries:
            if y < B:
                ans.append(suf[y][x] % MOD)
            else:
                t = 0
                i = x
                while i < n:
                    t += nums[i]
                    i += y
                ans.append(t % MOD)
        return ans
# @lc code=end
