#
# @lc app=leetcode id=3179 lang=python3
#
# [3179] Find the N-th Value After K Seconds
#
# https://leetcode.com/problems/find-the-n-th-value-after-k-seconds/description/
#
# algorithms
# Medium (54.12%)
# Likes:    133
# Dislikes: 21
# Total Accepted:    47.8K
# Total Submissions: 88.3K
# Testcase Example:  "4\n5"
#
#
# You are given two integers n and k.
#
# Initially, you start with an array a of n integers where a[i] = 1 for
# all 0 <= i <= n - 1. After each second, you simultaneously update each
# element to be the sum of all its preceding elements plus the element
# itself. For example, after one second, a[0] remains the same, a[1]
# becomes a[0] + a[1], a[2] becomes a[0] + a[1] + a[2], and so on.
#
# Return the value of a[n - 1] after k seconds.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 4, k = 5
#
# Output: 56
#
# Explanation:
#
#                         Second
#                         State After
#
#                         0
#                         [1,1,1,1]
#
#                         1
#                         [1,2,3,4]
#
#                         2
#                         [1,3,6,10]
#
#                         3
#                         [1,4,10,20]
#
#                         4
#                         [1,5,15,35]
#
#                         5
#                         [1,6,21,56]
#
# Example 2:
#
# Input: n = 5, k = 3
#
# Output: 35
#
# Explanation:
#
#                         Second
#                         State After
#
#                         0
#                         [1,1,1,1,1]
#
#                         1
#                         [1,2,3,4,5]
#
#                         2
#                         [1,3,6,10,15]
#
#                         3
#                         [1,4,10,20,35]
#
# Constraints:
#
# 1 <= n, k <= 1000
#

# @lc code=start
class Solution:
    def valueAfterKSeconds(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Each second replaces a with its prefix sums. After k seconds, a[n-1]
        equals C(n+k-1, n-1) (combinations / hockey-stick identity).

        Algorithm:
        - Simulate k rounds of in-place prefix sums modulo 1e9+7 (n,k <= 1000).

        Complexity: O(n * k) time, O(n) space.
        """
        MOD = 10**9 + 7
        a = [1] * n
        for _ in range(k):
            for i in range(1, n):
                a[i] = (a[i] + a[i - 1]) % MOD
        return a[-1]

    def valueAfterKSeconds_binom(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Alternate closed form: a[n-1] after k seconds is C(n+k-1, k) mod 1e9+7.

        Algorithm:
        - Compute binomial via multiplicative formula.

        Complexity: O(min(n, k)) time, O(1) space.
        """
        MOD = 10**9 + 7

        def comb(N: int, R: int) -> int:
            R = min(R, N - R)
            num = den = 1
            for i in range(R):
                num = num * (N - i) % MOD
                den = den * (i + 1) % MOD
            return num * pow(den, MOD - 2, MOD) % MOD

        return comb(n + k - 1, k)
# @lc code=end
