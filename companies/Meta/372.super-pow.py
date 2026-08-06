#
# @lc app=leetcode id=372 lang=python3
#
# [372] Super Pow
#
# https://leetcode.com/problems/super-pow/description/
#
# algorithms
# Medium (37.27%)
# Likes:    1106
# Dislikes: 1489
# Total Accepted:    109K
# Total Submissions: 293K
# Testcase Example:  "2"
#
# Your task is to calculate a^b mod 1337 where a is a positive integer and b is
# an extremely large positive integer given in the form of an array.
#
# Example 1:
#
# Input: a = 2, b = [3]
# Output: 8
#
# Example 2:
#
# Input: a = 2, b = [1,0]
# Output: 1024
#
# Example 3:
#
# Input: a = 1, b = [4,3,3,8,5,2]
# Output: 1
#
# Constraints:
#
# 1 <= a <= 2^31 - 1
#
# 1 <= b.length <= 2000
#
# 0 <= b[i] <= 9
#
# b does not contain leading zeros.
#

# @lc code=start
from typing import List


class Solution:
    def superPow(self, a: int, b: List[int]) -> int:
        """
        Interview explanation:
        Compute a^b mod 1337 where b is a huge digit array. Use modular
        exponentiation digit-by-digit: a^[d0..dk] =
        (a^[d0..d{k-1}])^10 * a^dk (mod 1337).
        1337 = 7 * 191; Euler φ(1337) = 1140 also enables reducing the
        exponent when gcd(a, 1337) == 1 (see superPowEuler).

        Algorithm:
        - For each digit d in b: result = pow(result, 10, MOD) * pow(a, d, MOD) % MOD
        - Return result.

        Complexity: O(len(b) * log MOD) with built-in pow, O(1) space.
        """
        MOD = 1337
        result = 1
        for digit in b:
            result = pow(result, 10, MOD) * pow(a, digit, MOD) % MOD
        return result

    def superPowEuler(self, a: int, b: List[int]) -> int:
        """
        Interview explanation:
        Alternate: Euler's theorem. φ(1337) = 1140. When gcd(a, 1337) == 1,
        a^e ≡ a^(e mod 1140) (mod 1337). Otherwise fall back to digit pow,
        or reduce exponent carefully with CRT / direct pow of the big int.

        Algorithm:
        - Build exp = int(''.join(map(str, b))) % 1140 if gcd(a%1337, 1337)==1
          else use full digit method; here we reduce b mod φ when coprime,
          else use digit-by-digit (always correct).

        Complexity: O(len(b)) to reduce exponent + O(log exp) pow.
        """
        MOD = 1337
        PHI = 1140  # φ(7)*φ(191) = 6*190
        a %= MOD
        if a == 0:
            return 0
        # Always-correct path via digit reduction using φ only when coprime.
        from math import gcd

        if gcd(a, MOD) == 1:
            exp = 0
            for digit in b:
                exp = (exp * 10 + digit) % PHI
            # a^φ ≡ 1, but if exp becomes 0 and b != 0, use φ (a^φ ≡ 1).
            if exp == 0 and any(b):
                exp = PHI
            return pow(a, exp, MOD)
        return self.superPow(a, b)
# @lc code=end
