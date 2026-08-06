#
# @lc app=leetcode id=1388 lang=python3
#
# [1388] Pizza With 3n Slices
#
# https://leetcode.com/problems/pizza-with-3n-slices/description/
#
# algorithms
# Hard (54.18%)
# Likes:    1149
# Dislikes: 24
# Total Accepted:    39.7K
# Total Submissions: 73.3K
# Testcase Example:  "[1,2,3,4,5,6]"
#
# There is a pizza with 3n slices of varying size, you and your friends will
# take slices of pizza as follows:
#
# You will pick any pizza slice.
#
# Your friend Alice will pick the next slice in the anti-clockwise direction of
# your pick.
#
# Your friend Bob will pick the next slice in the clockwise direction of your
# pick.
#
# Repeat until there are no more slices of pizzas.
#
# Given an integer array slices that represent the sizes of the pizza slices in
# a clockwise direction, return the maximum possible sum of slice sizes that
# you can pick.
#
# Example 1:
#
# Input: slices = [1,2,3,4,5,6]
# Output: 10
# Explanation: Pick pizza slice of size 4, Alice and Bob will pick slices with
# size 3 and 5 respectively. Then Pick slices with size 6, finally Alice and
# Bob will pick slice of size 2 and 1 respectively. Total = 4 + 6.
#
# Example 2:
#
# Input: slices = [8,9,8,6,1,1]
# Output: 16
# Explanation: Pick pizza slice of size 8 in each turn. If you pick slice with
# size 9 your partners will pick slices of size 8.
#
# Constraints:
#
# 3 * n == slices.length
#
# 1 <= slices.length <= 500
#
# 1 <= slices[i] <= 1000
#

# @lc code=start

from typing import List
from functools import lru_cache


class Solution:
    def maxSizeSlices(self, slices: List[int]) -> int:
        """
        Interview explanation:
        Circular array; pick n=len/3 non-adjacent slices maximizing sum
        (like house robber II on choosing n items).

        Algorithm:
        - DP: max sum picking exactly n non-adjacent from linear array
        - Answer = max(dp on slices[0..-2], dp on slices[1..])

        Complexity: O(n^2) time, O(n^2) or O(n) space.
        """
        def linear(arr: List[int], k: int) -> int:
            m = len(arr)
            dp = [[0] * (k + 1) for _ in range(m + 1)]
            for i in range(1, m + 1):
                for j in range(1, k + 1):
                    dp[i][j] = max(dp[i - 1][j], (dp[i - 2][j - 1] if i >= 2 else 0) + arr[i - 1])
            return dp[m][k]

        n = len(slices) // 3
        return max(linear(slices[:-1], n), linear(slices[1:], n))
# @lc code=end
