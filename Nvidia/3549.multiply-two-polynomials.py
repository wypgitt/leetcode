#
# @lc app=leetcode id=3549 lang=python3
#
# [3549] Multiply Two Polynomials
#
# https://leetcode.com/problems/multiply-two-polynomials/description/
#
# algorithms
# Hard (58.77%)
# Likes:    6
# Dislikes: 1
# Total Accepted:    422
# Total Submissions: 718
# Testcase Example:  "[3,2,5]\n[1,4]"
#
#
# You are given two integer arrays poly1 and poly2, where the element at
# index i in each array represents the coefficient of x^i in a polynomial.
#
# Let A(x) and B(x) be the polynomials represented by poly1 and poly2,
# respectively.
#
# Return an integer array result of length (poly1.length + poly2.length -
# 1) representing the coefficients of the product polynomial R(x) = A(x) *
# B(x), where result[i] denotes the coefficient of x^i in R(x).
#
# Example 1:
#
# Input: poly1 = [3,2,5], poly2 = [1,4]
#
# Output: [3,14,13,20]
#
# Explanation:
#
# A(x) = 3 + 2x + 5x^2 and B(x) = 1 + 4x
#
# R(x) = (3 + 2x + 5x^2) * (1 + 4x)
#
# R(x) = 3 * 1 + (3 * 4 + 2 * 1)x + (2 * 4 + 5 * 1)x^2 + (5 * 4)x^3
#
# R(x) = 3 + 14x + 13x^2 + 20x^3
#
# Thus, result = [3, 14, 13, 20].
#
# Example 2:
#
# Input: poly1 = [1,0,-2], poly2 = [-1]
#
# Output: [-1,0,2]
#
# Explanation:
#
# A(x) = 1 + 0x - 2x^2 and B(x) = -1
#
# R(x) = (1 + 0x - 2x^2) * (-1)
#
# R(x) = -1 + 0x + 2x^2
#
# Thus, result = [-1, 0, 2].
#
# Example 3:
#
# Input: poly1 = [1,5,-3], poly2 = [-4,2,0]
#
# Output: [-4,-18,22,-6,0]
#
# Explanation:
#
# A(x) = 1 + 5x - 3x^2 and B(x) = -4 + 2x + 0x^2
#
# R(x) = (1 + 5x - 3x^2) * (-4 + 2x + 0x^2)
#
# R(x) = 1 * -4 + (1 * 2 + 5 * -4)x + (5 * 2 + -3 * -4)x^2 + (-3 * 2)x^3 +
# 0x^4
#
# R(x) = -4 -18x + 22x^2 -6x^3 + 0x^4
#
# Thus, result = [-4, -18, 22, -6, 0].
#
# Constraints:
#
# 1 <= poly1.length, poly2.length <= 5 * 10^4
#
# -10^3 <= poly1[i], poly2[i] <= 10^3
#
# poly1 and poly2 contain at least one non-zero coefficient.
#

# @lc code=start
import math
from typing import List


class Solution:
    def multiply(self, poly1: List[int], poly2: List[int]) -> List[int]:
        """
        Interview explanation:
        Polynomial multiplication is convolution of coefficient arrays. With
        length up to 5e4, use FFT instead of the O(n^2) double loop.

        Algorithm:
        - Pad both polys to the next power of two ≥ len1+len2-1.
        - Forward FFT, pointwise multiply, inverse FFT; round real parts.

        Alternate: NTT with modular roots when coefficients are modular.
        Complexity: O(N log N) time, O(N) space (N = padded length).
        """
        m = len(poly1) + len(poly2) - 1
        n = 1
        while n < m:
            n <<= 1

        fa = list(map(complex, poly1)) + [0j] * (n - len(poly1))
        fb = list(map(complex, poly2)) + [0j] * (n - len(poly2))

        self._fft(fa, invert=False)
        self._fft(fb, invert=False)
        for i in range(n):
            fa[i] *= fb[i]
        self._fft(fa, invert=True)
        return [int(round(fa[i].real)) for i in range(m)]

    def _fft(self, a: List[complex], invert: bool) -> None:
        n = len(a)
        j = 0
        for i in range(1, n):
            bit = n >> 1
            while j & bit:
                j ^= bit
                bit >>= 1
            j ^= bit
            if i < j:
                a[i], a[j] = a[j], a[i]

        length = 2
        while length <= n:
            ang = 2 * math.pi / length * (-1 if invert else 1)
            wlen = complex(math.cos(ang), math.sin(ang))
            for i in range(0, n, length):
                w = 1 + 0j
                half = length // 2
                for j in range(i, i + half):
                    u = a[j]
                    v = a[j + half] * w
                    a[j] = u + v
                    a[j + half] = u - v
                    w *= wlen
            length <<= 1

        if invert:
            for i in range(n):
                a[i] /= n
# @lc code=end
