#
# @lc app=leetcode id=3916 lang=python3
#
# [3916] Number of ZigZag Arrays III
#
# https://leetcode.com/problems/number-of-zigzag-arrays-iii/description/
#
# algorithms
# Hard (63.53%)
# Likes:    2
# Dislikes: 2
# Total Accepted:    263
# Total Submissions: 414
# Testcase Example:  "3\n4\n5"
#
#
# You are given three integers n, l, and r.
#
# A ZigZag array of length n is defined as follows:
#
# Each element lies in the range [l, r].
#
# No two adjacent elements are equal.
#
# No three consecutive elements form a strictly increasing or strictly
# decreasing sequence.
#
# Return the total number of valid ZigZag arrays.
#
# Since the answer may be large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 3, l = 4, r = 5
#
# Output: 2
#
# Explanation:
#
# There are only 2 valid ZigZag arrays of length n = 3 using values in the
# range [4, 5]:
#
# [4, 5, 4]
#
# [5, 4, 5]
#
# Example 2:
#
# Input: n = 3, l = 1, r = 3
#
# Output: 10
#
# Explanation:
#
# There are 10 valid ZigZag arrays of length n = 3 using values in the
# range [1, 3]:
#
# [1, 2, 1], [1, 3, 1], [1, 3, 2]
#
# [2, 1, 2], [2, 1, 3], [2, 3, 1], [2, 3, 2]
#
# [3, 1, 2], [3, 1, 3], [3, 2, 3]
#
# All arrays meet the ZigZag conditions.
#
# Constraints:
#
# 3 <= n <= 200
#
# 1 <= l < r <= 10^​​​​​​​9
#

# @lc code=start
from typing import List


class Solution:
    MOD = 1_000_000_007

    def zigZagArrays(self, n: int, l: int, r: int) -> int:
        """
        Interview explanation:
        Count length-n arrays with values in [l, r], no equal adjacent, and no
        three consecutive strictly mono; answer mod 10^9+7. Value range can be
        huge, so use binomial-moment DP instead of O(m) states.

        Algorithm:
        - Let m = r-l+1. Track orientation starting with an up step (×2 at end).
        - Maintain binomial moments B[q] of the DP density; alternate up/down
          linear transforms using C(m, ·).
        - Precompute small binomials C(m, 0..n+1) modulo MOD.

        Complexity: O(n^2) time, O(n) space.
        """
        mod = self.MOD
        m = r - l + 1

        if n == 1:
            return m % mod

        choose_m = self._small_binoms(m, n + 1, mod)

        # Length 1: f[x] = 1, so B[q] = sum_x C(x, q) = C(m, q + 1).
        moments = [choose_m[q + 1] for q in range(n + 1)]

        # Count only the orientation whose first move is up:
        # step 1: up, step 2: down, step 3: up, ...
        for step in range(1, n):
            limit = n - step + 1
            nxt = [0] * limit

            if step % 2 == 1:
                # Up move:
                # new_B[q] = C(m, q + 1) * B[0] - B[q + 1] - B[q].
                total = moments[0]
                for q in range(limit):
                    nxt[q] = (choose_m[q + 1] * total - moments[q + 1] - moments[q]) % mod
            else:
                # Down move:
                # new_B[q] = B[q + 1].
                for q in range(limit):
                    nxt[q] = moments[q + 1]

            moments = nxt

        return (2 * moments[0]) % mod

    def _small_binoms(self, top: int, max_k: int, mod: int) -> List[int]:
        """
        Interview explanation:
        Compute C(top, k) for k = 0..max_k modulo mod (max_k < mod).

        Algorithm:
        - Precompute modular inverses 1..max_k; multiply iteratively
          C *= (top-k+1) * inv[k].

        Complexity: O(max_k) time, O(max_k) space.
        """
        top %= mod
        inv = [0] * (max_k + 1)
        if max_k >= 1:
            inv[1] = 1
        for x in range(2, max_k + 1):
            inv[x] = mod - (mod // x) * inv[mod % x] % mod

        out = [0] * (max_k + 1)
        out[0] = 1
        for k in range(1, max_k + 1):
            out[k] = out[k - 1] * ((top - k + 1) % mod) % mod * inv[k] % mod
        return out
# @lc code=end
