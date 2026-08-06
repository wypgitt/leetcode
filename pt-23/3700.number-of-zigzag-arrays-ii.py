#
# @lc app=leetcode id=3700 lang=python3
#
# [3700] Number of ZigZag Arrays II
#
# https://leetcode.com/problems/number-of-zigzag-arrays-ii/description/
#
# algorithms
# Hard (67.23%)
# Likes:    160
# Dislikes: 25
# Total Accepted:    72.7K
# Total Submissions: 108.1K
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
# A sequence is said to be strictly increasing if each element is strictly
# greater than its previous one (if exists).
#
# A sequence is said to be strictly decreasing if each element is strictly
# smaller than its previous one (if exists).
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
# ​​​​​​​There are 10 valid ZigZag arrays of length n = 3 using values in
# the range [1, 3]:
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
# 3 <= n <= 10^9
#
# 1 <= l < r <= 75​​​​​​​
#

# @lc code=start

class Solution:
    def zigZagArrays(self, n: int, l: int, r: int) -> int:
        """
        Interview explanation:
        Same alternating-direction DP as ZigZag I, but n is huge while
        m = r-l+1 <= 75, so the linear transition is applied via matrix
        exponentiation.

        Algorithm:
        - State vector [U|D] of size 2m from length-2 initialization.
        - Build transition T for newU/newD prefix-sum rules; compute T^(n-2)
          and multiply; sum entries mod 10^9+7.

        Complexity: O(m^3 log n) time, O(m^2) space.
        """
        MOD = 10**9 + 7
        m = r - l + 1
        size = 2 * m

        def mat_mul(a, b):
            res = [[0] * size for _ in range(size)]
            for i in range(size):
                for k in range(size):
                    if a[i][k] == 0:
                        continue
                    aik = a[i][k]
                    row = b[k]
                    out = res[i]
                    for j in range(size):
                        out[j] = (out[j] + aik * row[j]) % MOD
            return res

        def mat_vec(mat, vec):
            res = [0] * size
            for i in range(size):
                s = 0
                row = mat[i]
                for j in range(size):
                    s = (s + row[j] * vec[j]) % MOD
                res[i] = s
            return res

        def mat_pow(mat, exp):
            res = [[0] * size for _ in range(size)]
            for i in range(size):
                res[i][i] = 1
            while exp:
                if exp & 1:
                    res = mat_mul(res, mat)
                mat = mat_mul(mat, mat)
                exp >>= 1
            return res

        # T: newU[j] += D[k] (k < j); newD[j] += U[k] (k > j)
        T = [[0] * size for _ in range(size)]
        for j in range(m):
            for k in range(j):
                T[j][m + k] = 1  # newU[j] from D[k]
            for k in range(j + 1, m):
                T[m + j][k] = 1  # newD[j] from U[k]

        vec = [0] * size
        for j in range(m):
            vec[j] = j  # U
            vec[m + j] = m - 1 - j  # D

        if n == 2:
            return sum(vec) % MOD
        vec = mat_vec(mat_pow(T, n - 2), vec)
        return sum(vec) % MOD
# @lc code=end
