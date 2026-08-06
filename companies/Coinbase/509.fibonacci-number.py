#
# @lc app=leetcode id=509 lang=python3
#
# [509] Fibonacci Number
#
# https://leetcode.com/problems/fibonacci-number/description/
#
# algorithms
# Easy (74.48%)
# Likes:    9483
# Dislikes: 416
# Total Accepted:    3.3M
# Total Submissions: 4.4M
# Testcase Example:  "2"
#
# The Fibonacci numbers, commonly denoted F(n) form a sequence, called the
# Fibonacci sequence, such that each number is the sum of the two preceding
# ones, starting from 0 and 1. That is,
#
# F(0) = 0, F(1) = 1
# F(n) = F(n - 1) + F(n - 2), for n > 1.
#
# Given n, calculate F(n).
#
# Example 1:
#
# Input: n = 2
# Output: 1
# Explanation: F(2) = F(1) + F(0) = 1 + 0 = 1.
#
# Example 2:
#
# Input: n = 3
# Output: 2
# Explanation: F(3) = F(2) + F(1) = 1 + 1 = 2.
#
# Example 3:
#
# Input: n = 4
# Output: 3
# Explanation: F(4) = F(3) + F(2) = 2 + 1 = 3.
#
# Constraints:
#
# 0 <= n <= 30
#

# @lc code=start
class Solution:
    def fib(self, n: int) -> int:
        """
        Interview explanation:
        Classic DP / iterative: F(0)=0, F(1)=1, F(i)=F(i-1)+F(i-2). Roll two
        variables — O(1) space.

        Algorithm:
        - If n < 2: return n
        - a,b = 0,1; for _ in 2..n: a,b = b, a+b; return b.

        Complexity: O(n) time, O(1) space.
        """
        if n < 2:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def fib_matrix(self, n: int) -> int:
        """
        Interview explanation:
        Alternate classic: matrix exponentiation [[1,1],[1,0]]^(n) gives F(n).
        Fast doubling / binary exponentiation in O(log n).

        Algorithm:
        - Power [[1,1],[1,0]] to n via binary exp; return [0][1] (or [0][0] for F(n+1)).

        Complexity: O(log n) time, O(1) space.
        """
        if n < 2:
            return n

        def mul(A, B):
            return [
                [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
                [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]],
            ]

        def power(M, e):
            R = [[1, 0], [0, 1]]
            while e:
                if e & 1:
                    R = mul(R, M)
                M = mul(M, M)
                e >>= 1
            return R

        return power([[1, 1], [1, 0]], n)[0][1]
# @lc code=end
