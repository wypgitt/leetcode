#
# @lc app=leetcode id=1220 lang=python3
#
# [1220] Count Vowels Permutation
#
# https://leetcode.com/problems/count-vowels-permutation/description/
#
# algorithms
# Hard (61.34%)
# Likes:    3305
# Dislikes: 220
# Total Accepted:    186K
# Total Submissions: 303K
# Testcase Example:  "1"
#
# Given an integer n, your task is to count how many strings of length n can be
# formed under the following rules:
#
# Each character is a lower case vowel ('a', 'e', 'i', 'o', 'u')
#
# Each vowel 'a' may only be followed by an 'e'.
#
# Each vowel 'e' may only be followed by an 'a' or an 'i'.
#
# Each vowel 'i' may not be followed by another 'i'.
#
# Each vowel 'o' may only be followed by an 'i' or a 'u'.
#
# Each vowel 'u' may only be followed by an 'a'.
#
# Since the answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 1
# Output: 5
# Explanation: All possible strings are: "a", "e", "i" , "o" and "u".
#
# Example 2:
#
# Input: n = 2
# Output: 10
# Explanation: All possible strings are: "ae", "ea", "ei", "ia", "ie", "io",
# "iu", "oi", "ou" and "ua".
#
# Example 3:
#
# Input: n = 5
# Output: 68
#
# Constraints:
#
# 1 <= n <= 2 * 10^4
#



# @lc code=start
class Solution:
    def countVowelPermutation(self, n: int) -> int:
        """
        Interview explanation:
        Count length-n vowel strings under transition rules:
        a→e, e→a/i, i→a/e/o/u, o→i/u, u→a. Maintain five DP counts.

        Algorithm:
        - Start all vowels=1; for n-1 steps apply transitions; sum mod 10^9+7

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        a = e = i = o = u = 1
        for _ in range(n - 1):
            a2 = e % MOD
            e2 = (a + i) % MOD
            i2 = (a + e + o + u) % MOD
            o2 = (i + u) % MOD
            u2 = a % MOD
            a, e, i, o, u = a2, e2, i2, o2, u2
        return (a + e + i + o + u) % MOD

    def countVowelPermutation_matrix(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: 5x5 transition matrix raised to n-1; sum all entries of
        T^{n-1} (each vowel starts with count 1).

        Algorithm:
        - T[to][from]=1 if edge from→to; matrix pow; sum all cells

        Complexity: O(log n) time, O(1) space.
        """
        MOD = 10**9 + 7
        # order a,e,i,o,u; T[j][i]=1 if i can go to j
        T = [
            [0, 1, 1, 0, 1],  # to a from e,i,u
            [1, 0, 1, 0, 0],  # to e from a,i
            [0, 1, 0, 1, 0],  # to i from e,o
            [0, 0, 1, 0, 0],  # to o from i
            [0, 0, 1, 1, 0],  # to u from i,o
        ]

        def mul(A, B):
            C = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    s = 0
                    for z in range(5):
                        s += A[x][z] * B[z][y]
                    C[x][y] = s % MOD
            return C

        def mpow(A, p):
            R = [[1 if x == y else 0 for y in range(5)] for x in range(5)]
            while p:
                if p & 1:
                    R = mul(R, A)
                A = mul(A, A)
                p >>= 1
            return R

        if n == 1:
            return 5
        Tn = mpow(T, n - 1)
        return sum(sum(row) for row in Tn) % MOD
# @lc code=end
