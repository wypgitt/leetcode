#
# @lc app=leetcode id=4002 lang=python3
#
# [4002] Count Valid Sequences
#
# https://leetcode.com/problems/count-valid-sequences/description/
#
# algorithms
# Medium (42.70%)
# Likes:    64
# Dislikes: 13
# Total Accepted:    13.1K
# Total Submissions: 30.6K
# Testcase Example:  "5\n3"
#
#
# You are given two positive integers n and k.
#
# A valid sequence is a sequence of k positive integers such that:
#
# The sum of all integers in the sequence is equal to n.
#
# The product of all integers in the sequence is even.
#
# Return the number of valid sequences. Since the answer may be very
# large, return it modulo 10^9​​​​​​​ + 7.
#
# Two sequences are considered different if they differ at any index. For
# example, [1, 1, 2] and [1, 2, 1] are considered different sequences.
#
# Example 1:
#
# Input: n = 5, k = 3
#
# Output: 3
#
# Explanation:
#
# The sequences of length k = 3 whose sum is 5 are:
#
#                         Sequence
#                         Product
#                         Parity
#
#                         [1, 1, 3]
#                         1 * 1 * 3 = 3
#                         Odd
#
#                         [1, 2, 2]
#                         1 * 2 * 2 = 4
#                         Even
#
#                         [2, 1, 2]
#                         2 * 1 * 2 = 4
#                         Even
#
#                         [2, 2, 1]
#                         2 * 2 * 1 = 4
#                         Even
#
#                         [1, 3, 1]
#                         1 * 3 * 1 = 3
#                         Odd
#
#                         [3, 1, 1]
#                         3 * 1 * 1 = 3
#                         Odd
#
# There are 3 sequences with an even product, thus the answer is 3.
#
# Example 2:
#
# Input: n = 3, k = 2
#
# Output: 2
#
# Explanation:
#
# The sequences of length k = 2 whose sum is 3 are:
#
#                         Sequence
#                         Product
#                         Parity
#
#                         [1, 2]
#                         1 * 2 = 2
#                         Even
#
#                         [2, 1]
#                         2 * 1 = 2
#                         Even
#
# There are 2 sequences with an even product, thus the answer is 2.
#
# Example 3:
#
# Input: n = 5, k = 5
#
# Output: 0
#
# Explanation:
#
# The only possible sequence of length k = 5 whose sum is 5 is [1, 1, 1,
# 1, 1], which has an odd product. Thus, the answer is 0.
#
# Constraints:
#
# 1 <= n <= 5 * 10^5
#
# 1 <= k <= n
#

# @lc code=start
MX = 5 * 10**5 + 1
MOD = 10**9 + 7
_fact = [1] * MX
_inv = [1] * MX
for _i in range(1, MX):
    _fact[_i] = _fact[_i - 1] * _i % MOD
    _inv[_i] = pow(_fact[_i], MOD - 2, MOD)


def _comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return _fact[n] * _inv[k] % MOD * _inv[n - k] % MOD


class Solution:
    def countValidSequences(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Count compositions of n into k positive parts with even product, i.e.
        at least one even part. Total compositions are C(n-1, k-1); subtract
        the all-odd ones.

        Algorithm:
        - Total = C(n-1, k-1).
        - All-odd k-tuples summing to n exist iff n and k have the same
          parity: write each part as 2*y_i+1 => sum y = (n-k)/2, count
          C((n-k)/2 + k - 1, k - 1) = C((n+k)/2 - 1, k - 1).
        - Answer = total - all_odd (mod 10^9+7).

        Complexity: O(N) preprocess once, O(1) / O(log MOD) per query.
        """
        ans = _comb(n - 1, k - 1)
        if (n + k) % 2 == 0:
            ans = (ans - _comb((n + k) // 2 - 1, k - 1)) % MOD
        return ans
# @lc code=end
