#
# @lc app=leetcode id=1444 lang=python3
#
# [1444] Number of Ways of Cutting a Pizza
#
# https://leetcode.com/problems/number-of-ways-of-cutting-a-pizza/description/
#
# algorithms
# Hard (61.6%)
# Likes:    1926
# Dislikes: 98
# Total Accepted:    77.9K
# Total Submissions: 126K
# Testcase Example:  "[\"A..\",\"AAA\",\"...\"]"
#
# Given a rectangular pizza represented as a rows x cols matrix containing the
# following characters: 'A' (an apple) and '.' (empty cell) and given the
# integer k. You have to cut the pizza into k pieces using k-1 cuts.
#
# For each cut you choose the direction: vertical or horizontal, then you
# choose a cut position at the cell boundary and cut the pizza into two pieces.
# If you cut the pizza vertically, give the left part of the pizza to a person.
# If you cut the pizza horizontally, give the upper part of the pizza to a
# person. Give the last piece of pizza to the last person.
#
# Return the number of ways of cutting the pizza such that each piece contains
# at least one apple. Since the answer can be a huge number, return this modulo
# 10^9 + 7.
#
# Example 1:
#
# Input: pizza = ["A..","AAA","..."], k = 3
# Output: 3
# Explanation: The figure above shows the three ways to cut the pizza. Note
# that pieces must contain at least one apple.
#
# Example 2:
#
# Input: pizza = ["A..","AA.","..."], k = 3
# Output: 1
#
# Example 3:
#
# Input: pizza = ["A..","A..","..."], k = 1
# Output: 1
#
# Constraints:
#
# 1 <= rows, cols <= 50
#
# rows == pizza.length
#
# cols == pizza[i].length
#
# 1 <= k <= 10
#
# pizza consists of characters 'A' and '.' only.
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def ways(self, pizza: List[str], k: int) -> int:
        """
        Interview explanation:
        Cut pizza into k pieces with k-1 cuts (horizontal or vertical), each
        piece must contain an apple. DP on top-left of remaining rectangle and
        cuts left; prefix sums of apples for O(1) queries.

        Algorithm:
        (DP + prefix)
        - apples[r][c] = count in sub-pizza (r.., c..); dfs(r,c,cuts): try cuts.

        Complexity: O(k * rows * cols * (rows+cols)) time, O(k*rows*cols) space.
        """
        MOD = 10**9 + 7
        rows, cols = len(pizza), len(pizza[0])
        apples = [[0] * (cols + 1) for _ in range(rows + 1)]
        for r in range(rows - 1, -1, -1):
            for c in range(cols - 1, -1, -1):
                apples[r][c] = (
                    (pizza[r][c] == "A")
                    + apples[r + 1][c]
                    + apples[r][c + 1]
                    - apples[r + 1][c + 1]
                )

        @lru_cache(None)
        def dfs(r: int, c: int, cuts: int) -> int:
            if apples[r][c] == 0:
                return 0
            if cuts == 0:
                return 1
            ans = 0
            # horizontal cut below row nr-1
            for nr in range(r + 1, rows):
                if apples[r][c] - apples[nr][c] > 0:
                    ans = (ans + dfs(nr, c, cuts - 1)) % MOD
            for nc in range(c + 1, cols):
                if apples[r][c] - apples[r][nc] > 0:
                    ans = (ans + dfs(r, nc, cuts - 1)) % MOD
            return ans

        return dfs(0, 0, k - 1)

    def ways_bottomup(self, pizza: List[str], k: int) -> int:
        """
        Interview explanation:
        Alternate bottom-up DP with same apple prefix: dp[cuts][r][c].

        Algorithm:
        - Initialize cuts=0; iterate cuts upward with cut transitions.

        Complexity: same O(k R C (R+C)).
        """
        MOD = 10**9 + 7
        R, C = len(pizza), len(pizza[0])
        apples = [[0] * (C + 1) for _ in range(R + 1)]
        for r in range(R - 1, -1, -1):
            for c in range(C - 1, -1, -1):
                apples[r][c] = (
                    (pizza[r][c] == "A")
                    + apples[r + 1][c]
                    + apples[r][c + 1]
                    - apples[r + 1][c + 1]
                )
        dp = [[[0] * C for _ in range(R)] for _ in range(k)]
        for r in range(R):
            for c in range(C):
                dp[0][r][c] = 1 if apples[r][c] > 0 else 0
        for cuts in range(1, k):
            for r in range(R):
                for c in range(C):
                    ans = 0
                    for nr in range(r + 1, R):
                        if apples[r][c] - apples[nr][c] > 0:
                            ans = (ans + dp[cuts - 1][nr][c]) % MOD
                    for nc in range(c + 1, C):
                        if apples[r][c] - apples[r][nc] > 0:
                            ans = (ans + dp[cuts - 1][r][nc]) % MOD
                    dp[cuts][r][c] = ans
        return dp[k - 1][0][0]
# @lc code=end
