#
# @lc app=leetcode id=3165 lang=python3
#
# [3165] Maximum Sum of Subsequence With Non-adjacent Elements
#
# https://leetcode.com/problems/maximum-sum-of-subsequence-with-non-adjacent-elements/description/
#
# algorithms
# Hard (15.72%)
# Likes:    166
# Dislikes: 32
# Total Accepted:    9.4K
# Total Submissions: 59.5K
# Testcase Example:  "[3,5,9]\n[[1,-2],[0,-3]]"
#
#
# You are given an array nums consisting of integers. You are also given a
# 2D array queries, where queries[i] = [pos_i, x_i].
#
# For query i, we first set nums[pos_i] equal to x_i, then we calculate
# the answer to query i which is the maximum sum of a subsequence of nums
# where no two adjacent elements are selected.
#
# Return the sum of the answers to all queries.
#
# Since the final answer may be very large, return it modulo 10^9 + 7.
#
# A subsequence is an array that can be derived from another array by
# deleting some or no elements without changing the order of the remaining
# elements.
#
# Example 1:
#
# Input: nums = [3,5,9], queries = [[1,-2],[0,-3]]
#
# Output: 21
#
# Explanation:
#
# After the 1^st query, nums = [3,-2,9] and the maximum sum of a
# subsequence with non-adjacent elements is 3 + 9 = 12.
#
# After the 2^nd query, nums = [-3,-2,9] and the maximum sum of a
# subsequence with non-adjacent elements is 9.
#
# Example 2:
#
# Input: nums = [0,-1], queries = [[0,-5]]
#
# Output: 0
#
# Explanation:
#
# After the 1^st query, nums = [-5,-1] and the maximum sum of a
# subsequence with non-adjacent elements is 0 (choosing an empty
# subsequence).
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^4
#
# -10^5 <= nums[i] <= 10^5
#
# 1 <= queries.length <= 5 * 10^4
#
# queries[i] == [pos_i, x_i]
#
# 0 <= pos_i <= nums.length - 1
#
# -10^5 <= x_i <= 10^5
#

# @lc code=start
from typing import List, Tuple


class Solution:
    def maximumSumSubsequence(self, nums: List[int], queries: List[List[int]]) -> int:
        """
        Interview explanation:
        After each point update, answer the classic non-adjacent max-subsequence
        sum (house robber, empty allowed). Many queries => segment tree where
        each node stores 4 endpoint-constrained best sums.

        Algorithm:
        - Node state (s00,s01,s10,s11): best sum with left/right ends taken or not.
        - Leaf x: (0, -inf, -inf, x). Merge forbids taking both abutting ends.
        - Query answer = max(0, all four states of root); sum answers mod 1e9+7.

        Complexity: O((n + q) log n) time, O(n) space.
        """
        MOD = 10**9 + 7
        NEG = -10**18
        n = len(nums)
        tree: list[Tuple[int, int, int, int]] = [(0, NEG, NEG, 0)] * (4 * n)

        def combine(
            a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]
        ) -> Tuple[int, int, int, int]:
            a00, a01, a10, a11 = a
            b00, b01, b10, b11 = b
            return (
                max(a00 + b00, a00 + b10, a01 + b00),
                max(a00 + b01, a00 + b11, a01 + b01),
                max(a10 + b00, a10 + b10, a11 + b00),
                max(a10 + b01, a10 + b11, a11 + b01),
            )

        def build(idx: int, l: int, r: int) -> None:
            if l == r:
                x = nums[l]
                tree[idx] = (0, NEG, NEG, x)
                return
            mid = (l + r) // 2
            build(idx * 2, l, mid)
            build(idx * 2 + 1, mid + 1, r)
            tree[idx] = combine(tree[idx * 2], tree[idx * 2 + 1])

        def update(idx: int, l: int, r: int, pos: int, val: int) -> None:
            if l == r:
                tree[idx] = (0, NEG, NEG, val)
                return
            mid = (l + r) // 2
            if pos <= mid:
                update(idx * 2, l, mid, pos, val)
            else:
                update(idx * 2 + 1, mid + 1, r, pos, val)
            tree[idx] = combine(tree[idx * 2], tree[idx * 2 + 1])

        build(1, 0, n - 1)
        ans = 0
        for pos, x in queries:
            update(1, 0, n - 1, pos, x)
            s00, s01, s10, s11 = tree[1]
            ans = (ans + max(0, s00, s01, s10, s11)) % MOD
        return ans

    def maximumSumSubsequence_dp(self, nums: List[int], queries: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate for small n: after each update, run linear house-robber DP.
        Too slow for the full constraints; useful as a correctness check.

        Algorithm:
        - take/skip DP: skip' = max(skip,take); take' = skip + max(0,x) style
          with empty allowed via max(0, ...).

        Complexity: O(n * q) time, O(1) extra space.
        """
        MOD = 10**9 + 7
        a = nums[:]
        total = 0
        for pos, x in queries:
            a[pos] = x
            take = skip = 0
            for v in a:
                take, skip = skip + v, max(skip, take)
            total = (total + max(0, take, skip)) % MOD
        return total
# @lc code=end
