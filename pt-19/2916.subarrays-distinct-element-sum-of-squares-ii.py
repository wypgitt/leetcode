#
# @lc app=leetcode id=2916 lang=python3
#
# [2916] Subarrays Distinct Element Sum of Squares II
#
# https://leetcode.com/problems/subarrays-distinct-element-sum-of-squares-ii/description/
#
# algorithms
# Hard (23.25%)
# Likes:    159
# Dislikes: 12
# Total Accepted:    5K
# Total Submissions: 21.3K
# Testcase Example:  "[1,2,1]"
#
#
# You are given a 0-indexed integer array nums.
#
# The distinct count of a subarray of nums is defined as:
#
# Let nums[i..j] be a subarray of nums consisting of all the indices from
# i to j such that 0 <= i <= j < nums.length. Then the number of distinct
# values in nums[i..j] is called the distinct count of nums[i..j].
#
# Return the sum of the squares of distinct counts of all subarrays of
# nums.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# A subarray is a contiguous non-empty sequence of elements within an
# array.
#
# Example 1:
#
# Input: nums = [1,2,1]
# Output: 15
# Explanation: Six possible subarrays are:
# [1]: 1 distinct value
# [2]: 1 distinct value
# [1]: 1 distinct value
# [1,2]: 2 distinct values
# [2,1]: 2 distinct values
# [1,2,1]: 2 distinct values
# The sum of the squares of the distinct counts in all subarrays is equal
# to 1^2 + 1^2 + 1^2 + 2^2 + 2^2 + 2^2 = 15.
#
# Example 2:
#
# Input: nums = [2,2]
# Output: 3
# Explanation: Three possible subarrays are:
# [2]: 1 distinct value
# [2]: 1 distinct value
# [2,2]: 1 distinct value
# The sum of the squares of the distinct counts in all subarrays is equal
# to 1^2 + 1^2 + 1^2 = 3.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def sumCounts(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same as I: sum of (distinct count)^2 over all subarrays, mod 10^9+7,
        but n <= 1e5.

        Algorithm:
        - Extend right endpoint r. nums[r] is newly distinct for starts in
          (prev[nums[r]], r]. Range-add +1 on those distinct counts.
        - Segment tree stores sum and sum-of-squares with lazy range add;
          after each r, add current sum-of-squares over all starts.

        Complexity: O(n log n) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        # segment tree over start indices 0..n-1
        tree_sum = [0] * (4 * n)
        tree_sq = [0] * (4 * n)
        lazy = [0] * (4 * n)

        def apply(node: int, lo: int, hi: int, v: int) -> None:
            length = hi - lo + 1
            tree_sq[node] = (tree_sq[node] + 2 * v * tree_sum[node] + v * v * length) % MOD
            tree_sum[node] = (tree_sum[node] + v * length) % MOD
            lazy[node] = (lazy[node] + v) % MOD

        def push(node: int, lo: int, hi: int) -> None:
            if lazy[node] and lo != hi:
                mid = (lo + hi) // 2
                apply(node * 2, lo, mid, lazy[node])
                apply(node * 2 + 1, mid + 1, hi, lazy[node])
                lazy[node] = 0

        def update(node: int, lo: int, hi: int, L: int, R: int, v: int) -> None:
            if L > hi or R < lo:
                return
            if L <= lo and hi <= R:
                apply(node, lo, hi, v)
                return
            push(node, lo, hi)
            mid = (lo + hi) // 2
            update(node * 2, lo, mid, L, R, v)
            update(node * 2 + 1, mid + 1, hi, L, R, v)
            tree_sum[node] = (tree_sum[node * 2] + tree_sum[node * 2 + 1]) % MOD
            tree_sq[node] = (tree_sq[node * 2] + tree_sq[node * 2 + 1]) % MOD

        last = {}
        ans = 0
        for r, x in enumerate(nums):
            prev = last.get(x, -1)
            # starts in (prev, r] i.e. prev+1 .. r
            update(1, 0, n - 1, prev + 1, r, 1)
            last[x] = r
            ans = (ans + tree_sq[1]) % MOD
        return ans
# @lc code=end
