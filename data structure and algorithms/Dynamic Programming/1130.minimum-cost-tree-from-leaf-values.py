#
# @lc app=leetcode id=1130 lang=python3
#
# [1130] Minimum Cost Tree From Leaf Values
#
# https://leetcode.com/problems/minimum-cost-tree-from-leaf-values/description/
#
# algorithms
# Medium (67.94%)
# Likes:    4462
# Dislikes: 283
# Total Accepted:    124K
# Total Submissions: 183K
# Testcase Example:  "[6,2,4]"
#
# Given an array arr of positive integers, consider all binary trees such that:
#
# Each node has either 0 or 2 children;
#
# The values of arr correspond to the values of each leaf in an in-order
# traversal of the tree.
#
# The value of each non-leaf node is equal to the product of the largest leaf
# value in its left and right subtree, respectively.
#
# Among all possible binary trees considered, return the smallest possible sum
# of the values of each non-leaf node. It is guaranteed this sum fits into a
# 32-bit integer.
#
# A node is a leaf if and only if it has zero children.
#
# Example 1:
#
# Input: arr = [6,2,4]
# Output: 32
# Explanation: There are two possible trees shown.
# The first has a non-leaf node sum 36, and the second has non-leaf node sum
# 32.
#
# Example 2:
#
# Input: arr = [4,11]
# Output: 44
#
# Constraints:
#
# 2 <= arr.length <= 40
#
# 1 <= arr[i] <= 15
#
# It is guaranteed that the answer fits into a 32-bit signed integer (i.e., it
# is less than 2^31).
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def mctFromLeafValues(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Cost of combining two subtrees is product of their max leaves. Greedy
        stack: always remove a local minimum next to a smaller neighbor —
        classic O(n) monotone stack optimal approach.

        Algorithm (stack):
        - Maintain decreasing stack; when arr[i] >= stack.top, pop mid and add
          mid * min(left_neighbor, arr[i]).
        - Drain remaining pairs.

        Complexity: O(n) time, O(n) space.
        """
        stack = [float("inf")]
        res = 0
        for x in arr:
            while stack[-1] <= x:
                mid = stack.pop()
                res += mid * min(stack[-1], x)
            stack.append(x)
        while len(stack) > 2:
            res += stack.pop() * stack[-1]
        return int(res)

    def mctFromLeafValues_dp(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Classic DP alternate: interval DP on leaf array — try every split;
        cost = left + right + max(left)*max(right).

        Algorithm:
        - dp[i][j] = min cost for arr[i..j]; maxleaf[i][j] for products.

        Complexity: O(n^3) time, O(n^2) space.
        """
        n = len(arr)

        @lru_cache(None)
        def dp(i: int, j: int) -> int:
            if i == j:
                return 0
            best = float("inf")
            for k in range(i, j):
                best = min(
                    best,
                    dp(i, k) + dp(k + 1, j) + max(arr[i : k + 1]) * max(arr[k + 1 : j + 1]),
                )
            return int(best)

        return dp(0, n - 1)
# @lc code=end
