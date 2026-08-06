#
# @lc app=leetcode id=2992 lang=python3
#
# [2992] Number of Self-Divisible Permutations
#
# https://leetcode.com/problems/number-of-self-divisible-permutations/description/
#
# algorithms
# Medium (71.83%)
# Likes:    23
# Dislikes: 0
# Total Accepted:    2.4K
# Total Submissions: 3.3K
# Testcase Example:  "1"
#
#
# Given an integer n, return the number of permutations of the 1-indexed
# array nums = [1, 2, ..., n], such that it's self-divisible.
#
# A 1-indexed array a of length n is self-divisible if for every 1 <= i <=
# n, gcd(a[i], i) == 1.
#
# A permutation of an array is a rearrangement of the elements of that
# array, for example here are all of the permutations of the array [1, 2,
# 3]:
#
# [1, 2, 3]
#
# [1, 3, 2]
#
# [2, 1, 3]
#
# [2, 3, 1]
#
# [3, 1, 2]
#
# [3, 2, 1]
#
# Example 1:
#
# Input: n = 1
# Output: 1
# Explanation: The array [1] has only 1 permutation which is
# self-divisible.
#
# Example 2:
#
# Input: n = 2
# Output: 1
# Explanation: The array [1,2] has 2 permutations and only one of them is
# self-divisible:
# nums = [1,2]: This is not self-divisible since gcd(nums[2], 2) != 1.
# nums = [2,1]: This is self-divisible since gcd(nums[1], 1) == 1 and
# gcd(nums[2], 2) == 1.
#
# Example 3:
#
# Input: n = 3
# Output: 3
# Explanation: The array [1,2,3] has 3 self-divisble permutations:
# [1,3,2], [3,1,2], [2,3,1].
# It can be shown that the other 3 permutations are not self-divisible.
# Hence the answer is 3.
#
# Constraints:
#
# 1 <= n <= 12
#
# @lc code=start

from functools import cache
from math import gcd


class Solution:
    def selfDivisiblePermutationCount(self, n: int) -> int:
        """
        Interview explanation:
        Premium: count permutations of [1..n] where gcd(perm[i], i) == 1 for
        every 1-indexed position i. n <= 12.

        Algorithm:
        - Bitmask DP / memo DFS: mask = used values; place next index
          i = popcount(mask)+1 with unused j where gcd(i,j)==1.

        Complexity: O(n * 2^n) time and space.
        """

        @cache
        def dfs(mask: int) -> int:
            i = mask.bit_count() + 1
            if i > n:
                return 1
            ans = 0
            for j in range(1, n + 1):
                if (mask >> j & 1) == 0 and gcd(i, j) == 1:
                    ans += dfs(mask | 1 << j)
            return ans

        return dfs(0)

    def selfDivisiblePermutationCount_dp(self, n: int) -> int:
        """
        Interview explanation:
        Alternate iterative DP over masks (values 1..n in low bits).

        Algorithm:
        - f[mask] = ways to assign popcount(mask) positions using bits in mask;
          transition when gcd(position, value)==1.

        Complexity: O(n * 2^n) time, O(2^n) space.
        """
        f = [0] * (1 << n)
        f[0] = 1
        for mask in range(1 << n):
            i = mask.bit_count()
            for j in range(1, n + 1):
                if (mask >> (j - 1) & 1) == 1 and gcd(i, j) == 1:
                    f[mask] += f[mask ^ (1 << (j - 1))]
        return f[-1]
# @lc code=end
