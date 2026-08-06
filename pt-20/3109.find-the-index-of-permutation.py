#
# @lc app=leetcode id=3109 lang=python3
#
# [3109] Find the Index of Permutation
#
# https://leetcode.com/problems/find-the-index-of-permutation/description/
#
# algorithms
# Medium (37.22%)
# Likes:    16
# Dislikes: 5
# Total Accepted:    926
# Total Submissions: 2.5K
# Testcase Example:  "[1,2]"
#
#
# Given an array perm of length n which is a permutation of [1, 2, ...,
# n], return the index of perm in the lexicographically sorted array of
# all of the permutations of [1, 2, ..., n].
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: perm = [1,2]
#
# Output: 0
#
# Explanation:
#
# There are only two permutations in the following order:
#
# [1,2], [2,1]
#
# And [1,2] is at index 0.
#
# Example 2:
#
# Input: perm = [3,1,2]
#
# Output: 4
#
# Explanation:
#
# There are only six permutations in the following order:
#
# [1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]
#
# And [3,1,2] is at index 4.
#
# Constraints:
#
# 1 <= n == perm.length <= 10^5
#
# perm is a permutation of [1, 2, ..., n].
#

# @lc code=start
from typing import List


class FenwickTree:
    def __init__(self, n: int):
        """
        Interview explanation:
        Binary indexed tree for prefix sums over values 1..n (used/unused marks).

        Algorithm:
        - Allocate 1-indexed sum array of size n+1.

        Complexity: O(n) space.
        """
        self.sums = [0] * (n + 1)

    def add(self, i: int, delta: int) -> None:
        """
        Interview explanation:
        Point update: add delta at index i.

        Algorithm:
        - Walk i += i & -i updating fenwick nodes.

        Complexity: O(log n) time.
        """
        while i < len(self.sums):
            self.sums[i] += delta
            i += i & -i

    def get(self, i: int) -> int:
        """
        Interview explanation:
        Prefix sum query on [1..i].

        Algorithm:
        - Walk i -= i & -i accumulating node sums.

        Complexity: O(log n) time.
        """
        total = 0
        while i > 0:
            total += self.sums[i]
            i -= i & -i
        return total


class Solution:
    def getPermutationIndex(self, perm: List[int]) -> int:
        """
        Interview explanation:
        Index of perm among lex-sorted permutations of 1..n, modulo 10^9+7.

        Algorithm:
        - Factorial number system: at position i, add (# unused < perm[i]) * (n-1-i)!.
        - Fenwick tree marks used values; query prefix for unused smaller counts.

        Complexity: O(n log n) time, O(n) space.
        """
        mod = 10**9 + 7
        n = len(perm)
        ans = 0
        tree = FenwickTree(n)
        fact = [1] * (n + 1)
        for i in range(2, n + 1):
            fact[i] = fact[i - 1] * i % mod
        for i, num in enumerate(perm):
            unused = num - 1 - tree.get(num - 1)
            ans = (ans + unused * fact[n - 1 - i]) % mod
            tree.add(num, 1)
        return ans
# @lc code=end
