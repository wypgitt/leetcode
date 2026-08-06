#
# @lc app=leetcode id=935 lang=python3
#
# [935] Knight Dialer
#
# https://leetcode.com/problems/knight-dialer/description/
#
# algorithms
# Medium (62.07%)
# Likes:    3221
# Dislikes: 453
# Total Accepted:    204K
# Total Submissions: 329K
# Testcase Example:  "1"
#
# The chess knight has a unique movement, it may move two squares vertically
# and one square horizontally, or two squares horizontally and one square
# vertically (with both forming the shape of an L). The possible movements of
# chess knight are shown in this diagram:
#
# A chess knight can move as indicated in the chess diagram below:
#
# We have a chess knight and a phone pad as shown below, the knight can only
# stand on a numeric cell (i.e. blue cell).
#
# Given an integer n, return how many distinct phone numbers of length n we can
# dial.
#
# You are allowed to place the knight on any numeric cell initially and then
# you should perform n - 1 jumps to dial a number of length n. All jumps should
# be valid knight jumps.
#
# As the answer may be very large, return the answer modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 1
# Output: 10
# Explanation: We need to dial a number of length 1, so placing the knight over
# any numeric cell of the 10 cells is sufficient.
#
# Example 2:
#
# Input: n = 2
# Output: 20
# Explanation: All the valid number we can dial are [04, 06, 16, 18, 27, 29,
# 34, 38, 40, 43, 49, 60, 61, 67, 72, 76, 81, 83, 92, 94]
#
# Example 3:
#
# Input: n = 3131
# Output: 136006598
# Explanation: Please take care of the mod.
#
# Constraints:
#
# 1 <= n <= 5000
#

# @lc code=start
class Solution:
    def knightDialer(self, n: int) -> int:
        """
        Interview explanation:
        Knight on phone pad hops; count distinct n-length number sequences.
        DP: dp[d] = ways to be on digit d after hops; transition via knight moves.

        Algorithm (DP):
        - moves[d] = list of reachable digits from d (no 5→nothing special; * # unused)
        - dp = [1]*10; repeat n-1 times: ndp[v] += dp[u] for v in moves[u]
        - Return sum(dp) % MOD

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        moves = {
            0: [4, 6],
            1: [6, 8],
            2: [7, 9],
            3: [4, 8],
            4: [0, 3, 9],
            5: [],
            6: [0, 1, 7],
            7: [2, 6],
            8: [1, 3],
            9: [2, 4],
        }
        dp = [1] * 10
        for _ in range(n - 1):
            ndp = [0] * 10
            for u in range(10):
                for v in moves[u]:
                    ndp[v] = (ndp[v] + dp[u]) % MOD
            dp = ndp
        return sum(dp) % MOD

    def knightDialer_matrix(self, n: int) -> int:
        """
        Interview explanation:
        Alternate optimal: matrix exponentiation on the 10x10 transition graph
        for O(log n) hops (same recurrence).

        Algorithm:
        - Build adjacency matrix A; answer = sum((A^{n-1} * ones_vector))

        Complexity: O(d^3 log n) time with d=10, O(d^2) space.
        """
        MOD = 10**9 + 7
        moves = [
            [4, 6], [6, 8], [7, 9], [4, 8], [0, 3, 9],
            [], [0, 1, 7], [2, 6], [1, 3], [2, 4],
        ]
        A = [[0] * 10 for _ in range(10)]
        for u, vs in enumerate(moves):
            for v in vs:
                A[v][u] = 1

        def mul(X, Y):
            Z = [[0] * 10 for _ in range(10)]
            for i in range(10):
                for k in range(10):
                    if X[i][k]:
                        for j in range(10):
                            Z[i][j] = (Z[i][j] + X[i][k] * Y[k][j]) % MOD
            return Z

        def mpow(M, e):
            R = [[1 if i == j else 0 for j in range(10)] for i in range(10)]
            while e:
                if e & 1:
                    R = mul(R, M)
                M = mul(M, M)
                e >>= 1
            return R

        if n == 1:
            return 10
        P = mpow(A, n - 1)
        return sum(sum(row) % MOD for row in P) % MOD
# @lc code=end

