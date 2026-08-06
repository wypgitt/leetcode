#
# @lc app=leetcode id=3193 lang=python3
#
# [3193] Count the Number of Inversions
#
# https://leetcode.com/problems/count-the-number-of-inversions/description/
#
# algorithms
# Hard (32.05%)
# Likes:    200
# Dislikes: 37
# Total Accepted:    11.7K
# Total Submissions: 36.5K
# Testcase Example:  "3\n[[2,2],[0,0]]"
#
#
# You are given an integer n and a 2D array requirements, where
# requirements[i] = [end_i, cnt_i] represents the end index and the
# inversion count of each requirement.
#
# A pair of indices (i, j) from an integer array nums is called an
# inversion if:
#
# i < j and nums[i] > nums[j]
#
# Return the number of permutations perm of [0, 1, 2, ..., n - 1] such
# that for all requirements[i], perm[0..end_i] has exactly cnt_i
# inversions.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 3, requirements = [[2,2],[0,0]]
#
# Output: 2
#
# Explanation:
#
# The two permutations are:
#
# [2, 0, 1]
#
# Prefix [2, 0, 1] has inversions (0, 1) and (0, 2).
#
# Prefix [2] has 0 inversions.
#
# [1, 2, 0]
#
# Prefix [1, 2, 0] has inversions (0, 2) and (1, 2).
#
# Prefix [1] has 0 inversions.
#
# Example 2:
#
# Input: n = 3, requirements = [[2,2],[1,1],[0,0]]
#
# Output: 1
#
# Explanation:
#
# The only satisfying permutation is [2, 0, 1]:
#
# Prefix [2, 0, 1] has inversions (0, 1) and (0, 2).
#
# Prefix [2, 0] has an inversion (0, 1).
#
# Prefix [2] has 0 inversions.
#
# Example 3:
#
# Input: n = 2, requirements = [[0,0],[1,0]]
#
# Output: 1
#
# Explanation:
#
# The only satisfying permutation is [0, 1]:
#
# Prefix [0] has 0 inversions.
#
# Prefix [0, 1] has no inversions.
#
# Constraints:
#
# 2 <= n <= 300
#
# 1 <= requirements.length <= n
#
# requirements[i] = [end_i, cnt_i]
#
# 0 <= end_i <= n - 1
#
# 0 <= cnt_i <= 400
#
# The input is generated such that there is at least one i such that end_i
# == n - 1.
#
# The input is generated such that all end_i are unique.
#

# @lc code=start

from typing import List


class Solution:
    def numberOfPermutations(self, n: int, requirements: List[List[int]]) -> int:
        """
        Interview explanation:
        Count perms of 0..n-1 where each required prefix end has exact inversion
        count. Build perms by inserting n positions left-to-right.

        Algorithm:
        - f[i][j] = ways for length i+1 with j inversions.
        - Transition: new value creates k in [0..i] new inversions:
          f[i][j] += f[i-1][j-k].
        - At constrained ends, only keep the required cnt (others zero).

        Complexity: O(n * m * min(n,m)) time, O(n*m) space, m<=400.
        """
        req = [-1] * n
        for end, cnt in requirements:
            req[end] = cnt
        if req[0] > 0:
            return 0
        req[0] = 0
        MOD = 10**9 + 7
        m = max(req)
        f = [[0] * (m + 1) for _ in range(n)]
        f[0][0] = 1
        for i in range(1, n):
            lo, hi = 0, m
            if req[i] >= 0:
                lo = hi = req[i]
            for j in range(lo, hi + 1):
                s = 0
                for k in range(min(i, j) + 1):
                    s += f[i - 1][j - k]
                f[i][j] = s % MOD
        return f[n - 1][req[n - 1]]

    def numberOfPermutations_prefix(self, n: int, requirements: List[List[int]]) -> int:
        """
        Interview explanation:
        Same DP with prefix sums on the previous row to speed transitions to O(m).

        Algorithm:
        - pref[j+1] = sum f[i-1][0..j]; f[i][j] = pref[j+1]-pref[j-min(i,j)].

        Complexity: O(n*m) time, O(m) space with rolling arrays.
        """
        req = [-1] * n
        for end, cnt in requirements:
            req[end] = cnt
        if req[0] > 0:
            return 0
        req[0] = 0
        MOD = 10**9 + 7
        m = max(req)
        prev = [0] * (m + 1)
        prev[0] = 1
        for i in range(1, n):
            pref = [0] * (m + 2)
            for j in range(m + 1):
                pref[j + 1] = (pref[j] + prev[j]) % MOD
            cur = [0] * (m + 1)
            lo, hi = 0, m
            if req[i] >= 0:
                lo = hi = req[i]
            for j in range(lo, hi + 1):
                left = j - min(i, j)
                cur[j] = (pref[j + 1] - pref[left]) % MOD
            prev = cur
        return prev[req[n - 1]]
# @lc code=end
