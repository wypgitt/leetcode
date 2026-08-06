#
# @lc app=leetcode id=1137 lang=python3
#
# [1137] N-th Tribonacci Number
#
# https://leetcode.com/problems/n-th-tribonacci-number/description/
#
# algorithms
# Easy (63.09%)
# Likes:    4862
# Dislikes: 213
# Total Accepted:    1.1M
# Total Submissions: 1.8M
# Testcase Example:  "4"
#
# The Tribonacci sequence T_n is defined as follows:
#
# T_0 = 0, T_1 = 1, T_2 = 1, and T_n+3 = T_n + T_n+1 + T_n+2 for n >= 0.
#
# Given n, return the value of T_n.
#
# Example 1:
#
# Input: n = 4
# Output: 4
# Explanation:
# T_3 = 0 + 1 + 1 = 2
# T_4 = 1 + 1 + 2 = 4
#
# Example 2:
#
# Input: n = 25
# Output: 1389537
#
# Constraints:
#
# 0 <= n <= 37
#
# The answer is guaranteed to fit within a 32-bit integer, ie. answer <= 2^31 -
# 1.
#

# @lc code=start
class Solution:
    def tribonacci(self, n: int) -> int:
        """
        Interview explanation:
        T0=0, T1=1, T2=1, Tn=T(n-1)+T(n-2)+T(n-3). Iterative DP rolling three
        variables is the standard O(n) solution.

        Algorithm (DP):
        - If n<3 return [0,1,1][n]; else roll a,b,c.

        Complexity: O(n) time, O(1) space.
        """
        if n == 0:
            return 0
        if n <= 2:
            return 1
        a, b, c = 0, 1, 1
        for _ in range(3, n + 1):
            a, b, c = b, c, a + b + c
        return c

    def tribonacci_matrix(self, n: int) -> int:
        """
        Interview explanation:
        Optional classic alternate: matrix exponentiation for O(log n).
        [[1,1,1],[1,0,0],[0,1,0]]^n maps (T2,T1,T0) style recurrence.

        Algorithm:
        - For n==0 return 0; raise transition matrix to power n; extract T_n.

        Complexity: O(log n) time, O(1) space.
        """
        if n == 0:
            return 0
        if n <= 2:
            return 1

        def mul(A, B):
            C = [[0] * 3 for _ in range(3)]
            for i in range(3):
                for j in range(3):
                    C[i][j] = sum(A[i][k] * B[k][j] for k in range(3))
            return C

        def power(M, p):
            R = [[1 if i == j else 0 for j in range(3)] for i in range(3)]
            while p:
                if p & 1:
                    R = mul(R, M)
                M = mul(M, M)
                p >>= 1
            return R

        M = power([[1, 1, 1], [1, 0, 0], [0, 1, 0]], n - 2)
        # [T_n, T_{n-1}, T_{n-2}]^T = M * [T2, T1, T0]^T = M * [1,1,0]
        return M[0][0] * 1 + M[0][1] * 1 + M[0][2] * 0
# @lc code=end
