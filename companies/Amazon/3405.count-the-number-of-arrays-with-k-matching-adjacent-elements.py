#
# @lc app=leetcode id=3405 lang=python3
#
# [3405] Count the Number of Arrays with K Matching Adjacent Elements
#
# https://leetcode.com/problems/count-the-number-of-arrays-with-k-matching-adjacent-elements/description/
#
# algorithms
# Hard (58.23%)
# Likes:    431
# Dislikes: 68
# Total Accepted:    68.5K
# Total Submissions: 117.7K
# Testcase Example:  "3\n2\n1"
#
#
# You are given three integers n, m, k. A good array arr of size n is
# defined as follows:
#
# Each element in arr is in the inclusive range [1, m].
#
# Exactly k indices i (where 1 <= i < n) satisfy the condition arr[i - 1]
# == arr[i].
#
# Return the number of good arrays that can be formed.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 3, m = 2, k = 1
#
# Output: 4
#
# Explanation:
#
# There are 4 good arrays. They are [1, 1, 2], [1, 2, 2], [2, 1, 1] and
# [2, 2, 1].
#
# Hence, the answer is 4.
#
# Example 2:
#
# Input: n = 4, m = 2, k = 2
#
# Output: 6
#
# Explanation:
#
# The good arrays are [1, 1, 1, 2], [1, 1, 2, 2], [1, 2, 2, 2], [2, 1, 1,
# 1], [2, 2, 1, 1] and [2, 2, 2, 1].
#
# Hence, the answer is 6.
#
# Example 3:
#
# Input: n = 5, m = 2, k = 0
#
# Output: 2
#
# Explanation:
#
# The good arrays are [1, 2, 1, 2, 1] and [2, 1, 2, 1, 2]. Hence, the
# answer is 2.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# 1 <= m <= 10^5
#
# 0 <= k <= n - 1
#

# @lc code=start
class Solution:
    def countGoodArrays(self, n: int, m: int, k: int) -> int:
        """
        Interview explanation:
        Exactly k of the n-1 adjacent pairs are equal. Choose those k
        positions in C(n-1,k) ways; this forms n-k equal-runs. First run
        has m choices; each later run must differ from the previous (m-1).

        Algorithm:
        - Answer = C(n-1,k) * m * (m-1)^(n-k-1) mod 10^9+7.
        - Factorials + modular inverse for C; pow for the power.

        Complexity: O(n + log n) time, O(n) space.
        """
        MOD = 10**9 + 7
        return (
            m
            * pow(m - 1, n - k - 1, MOD)
            * self._comb(n - 1, k, MOD)
            % MOD
        )

    def _comb(self, n: int, k: int, MOD: int) -> int:
        if k < 0 or k > n:
            return 0
        fact = [1] * (n + 1)
        for i in range(1, n + 1):
            fact[i] = fact[i - 1] * i % MOD
        return (
            fact[n]
            * pow(fact[k], MOD - 2, MOD)
            % MOD
            * pow(fact[n - k], MOD - 2, MOD)
            % MOD
        )
# @lc code=end
