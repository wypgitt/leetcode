#
# @lc app=leetcode id=3344 lang=python3
#
# [3344] Maximum Sized Array
#
# https://leetcode.com/problems/maximum-sized-array/description/
#
# algorithms
# Medium (51.00%)
# Likes:    8
# Dislikes: 3
# Total Accepted:    666
# Total Submissions: 1.3K
# Testcase Example:  "10"
#
#
# Given a positive integer s, let A be a 3D array of dimensions n × n × n,
# where each element A[i][j][k] is defined as:
#
# A[i][j][k] = i * (j OR k), where 0 <= i, j, k < n.
#
# Return the maximum possible value of n such that the sum of all elements
# in array A does not exceed s.
#
# Example 1:
#
# Input: s = 10
#
# Output: 2
#
# Explanation:
#
# Elements of the array A for n = 2:
#
# A[0][0][0] = 0 * (0 OR 0) = 0
#
# A[0][0][1] = 0 * (0 OR 1) = 0
#
# A[0][1][0] = 0 * (1 OR 0) = 0
#
# A[0][1][1] = 0 * (1 OR 1) = 0
#
# A[1][0][0] = 1 * (0 OR 0) = 0
#
# A[1][0][1] = 1 * (0 OR 1) = 1
#
# A[1][1][0] = 1 * (1 OR 0) = 1
#
# A[1][1][1] = 1 * (1 OR 1) = 1
#
# The total sum of the elements in array A is 3, which does not exceed 10,
# so the maximum possible value of n is 2.
#
# Example 2:
#
# Input: s = 0
#
# Output: 1
#
# Explanation:
#
# Elements of the array A for n = 1:
#
# A[0][0][0] = 0 * (0 OR 0) = 0
#
# The total sum of the elements in array A is 0, which does not exceed 0,
# so the maximum possible value of n is 1.
#
# Constraints:
#
# 0 <= s <= 10^15
#

# @lc code=start

class Solution:
    _MX = 1330
    _f = None

    @classmethod
    def _init_f(cls) -> None:
        if cls._f is not None:
            return
        f = [0] * cls._MX
        for i in range(1, cls._MX):
            f[i] = f[i - 1] + i
            for j in range(i):
                f[i] += 2 * (i | j)
        cls._f = f

    def maxSizedArray(self, s: int) -> int:
        """
        Interview explanation:
        Sum_{i,j,k} i*(j|k) = (n(n-1)/2) * Sum_{j,k}(j|k). Sum of ORs for size n
        is monotone in n → binary search largest n with total ≤ s.

        Algorithm:
        - Precompute f[n] = Sum_{0≤j≤i<n}(i|j) adjusted so f[n-1]*(n-1)*n/2 is
          the full 3D sum (pair OR sum via symmetry).
        - Binary search n in [1, 1330].

        Complexity: O(MX^2) preprocess once, O(log MX) per query; O(MX) space.
        """
        self._init_f()
        f = self._f
        lo, hi = 1, self._MX
        while lo < hi:
            mid = (lo + hi + 1) >> 1
            if f[mid - 1] * (mid - 1) * mid // 2 <= s:
                lo = mid
            else:
                hi = mid - 1
        return lo

    def maxSizedArray_bitcount(self, s: int) -> int:
        """
        Interview explanation:
        Alternate: compute Sum(j|k) per bit (count numbers with bit set in
        [0,n)), then binary search without O(n^2) table.

        Algorithm:
        - For each bit, pairs with OR bit set = n^2 - unset^2; sum bits * 2^b.
        - Multiply by n(n-1)/2; binary search n.

        Complexity: O(B log S) per check × log n, O(1) space.
        """
        def array_sum(n: int) -> int:
            if n <= 1:
                return 0
            arith = n * (n - 1) // 2
            or_sum = 0
            bit = 0
            while (1 << bit) < n:
                group = 1 << (bit + 1)
                half = 1 << bit
                full = n // group
                rem = max(0, (n % group) - half)
                set_cnt = full * half + rem
                unset = n - set_cnt
                or_sum += (n * n - unset * unset) * (1 << bit)
                bit += 1
            return arith * or_sum

        lo, hi = 1, 1330
        while lo < hi:
            mid = (lo + hi + 1) >> 1
            if array_sum(mid) <= s:
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
