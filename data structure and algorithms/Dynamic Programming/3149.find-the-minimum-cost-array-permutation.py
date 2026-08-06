#
# @lc app=leetcode id=3149 lang=python3
#
# [3149] Find the Minimum Cost Array Permutation
#
# https://leetcode.com/problems/find-the-minimum-cost-array-permutation/description/
#
# algorithms
# Hard (26.23%)
# Likes:    155
# Dislikes: 8
# Total Accepted:    7.6K
# Total Submissions: 29K
# Testcase Example:  "[1,0,2]"
#
#
# You are given an array nums which is a permutation of [0, 1, 2, ..., n -
# 1]. The score of any permutation of [0, 1, 2, ..., n - 1] named perm is
# defined as:
#
# score(perm) = |perm[0] - nums[perm[1]]| + |perm[1] - nums[perm[2]]| +
# ... + |perm[n - 1] - nums[perm[0]]|
#
# Return the permutation perm which has the minimum possible score. If
# multiple permutations exist with this score, return the one that is
# lexicographically smallest among them.
#
# Example 1:
#
# Input: nums = [1,0,2]
#
# Output: [0,1,2]
#
# Explanation:
#
# The lexicographically smallest permutation with minimum cost is [0,1,2].
# The cost of this permutation is |0 - 0| + |1 - 2| + |2 - 1| = 2.
#
# Example 2:
#
# Input: nums = [0,2,1]
#
# Output: [0,2,1]
#
# Explanation:
#
# The lexicographically smallest permutation with minimum cost is [0,2,1].
# The cost of this permutation is |0 - 1| + |2 - 2| + |1 - 0| = 2.
#
# Constraints:
#
# 2 <= n == nums.length <= 14
#
# nums is a permutation of [0, 1, 2, ..., n - 1].
#

# @lc code=start
from functools import cache
from typing import List


class Solution:
    def findPermutation(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Score is a cycle cost with edge u -> v costing |u - nums[v]|. Find the
        lex-smallest permutation of 0..n-1 with minimum cycle score (n <= 14).

        Algorithm:
        - Score is rotation-invariant, so fix perm[0] = 0.
        - DP over subsets: dp(mask, last) = min remaining cost to visit all and
          return to 0.
        - Reconstruct by always appending the smallest next that preserves the
          optimal remaining cost.

        Complexity: O(n^2 * 2^n) time, O(n * 2^n) space.
        """
        n = len(nums)
        full = (1 << n) - 1

        @cache
        def dp(mask: int, last: int) -> int:
            if mask == full:
                return abs(last - nums[0])
            best = 10**9
            for nxt in range(n):
                if not (mask & (1 << nxt)):
                    best = min(
                        best,
                        abs(last - nums[nxt]) + dp(mask | (1 << nxt), nxt),
                    )
            return best

        mask, last, perm = 1, 0, [0]
        while len(perm) < n:
            target = dp(mask, last)
            for nxt in range(n):
                if mask & (1 << nxt):
                    continue
                if abs(last - nums[nxt]) + dp(mask | (1 << nxt), nxt) == target:
                    perm.append(nxt)
                    mask |= 1 << nxt
                    last = nxt
                    break
        return perm
# @lc code=end
