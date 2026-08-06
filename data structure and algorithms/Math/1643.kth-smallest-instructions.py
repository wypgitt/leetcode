#
# @lc app=leetcode id=1643 lang=python3
#
# [1643] Kth Smallest Instructions
#
# https://leetcode.com/problems/kth-smallest-instructions/description/
#
# algorithms
# Hard (44.6%)
# Likes:    572
# Dislikes: 17
# Total Accepted:    18.5K
# Total Submissions: 41.4K
# Testcase Example:  "[2,3]"
#
# Bob is standing at cell (0, 0), and he wants to reach destination: (row,
# column). He can only travel right and down. You are going to help Bob by
# providing instructions for him to reach destination.
#
# The instructions are represented as a string, where each character is either:
#
# 'H', meaning move horizontally (go right), or
#
# 'V', meaning move vertically (go down).
#
# Multiple instructions will lead Bob to destination. For example, if
# destination is (2, 3), both "HHHVV" and "HVHVH" are valid instructions.
#
# However, Bob is very picky. Bob has a lucky number k, and he wants the k^th
# lexicographically smallest instructions that will lead him to destination. k
# is 1-indexed.
#
# Given an integer array destination and an integer k, return the k^th
# lexicographically smallest instructions that will take Bob to destination.
#
# Example 1:
#
# Input: destination = [2,3], k = 1
# Output: "HHHVV"
# Explanation: All the instructions that reach (2, 3) in lexicographic order
# are as follows:
# ["HHHVV", "HHVHV", "HHVVH", "HVHHV", "HVHVH", "HVVHH", "VHHHV", "VHHVH",
# "VHVHH", "VVHHH"].
#
# Example 2:
#
# Input: destination = [2,3], k = 2
# Output: "HHVHV"
#
# Example 3:
#
# Input: destination = [2,3], k = 3
# Output: "HHVVH"
#
# Constraints:
#
# destination.length == 2
#
# 1 <= row, column <= 15
#
# 1 <= k <= nCr(row + column, row), where nCr(a, b) denotes a choose b.
#

# @lc code=start
from typing import List
import math


class Solution:
    def kthSmallestPath(self, destination: List[int], k: int) -> str:
        """
        Interview explanation:
        destination [row,col] needs `row` V and `col` H moves. Lex-smallest paths
        are those with H before V when possible. Choose k-th via combinatorics.

        Algorithm (combinatorics greedy):
        - Remaining v,h. If C(h+v-1, v) >= k, next must be 'H' (enough paths with H);
          else take 'V' and k -= that count.

        Complexity: O((h+v) * arithmetic) time, O(h+v) space for answer.
        """
        v, h = destination
        ans = []
        total = h + v
        for _ in range(total):
            if h == 0:
                ans.append("V")
                v -= 1
                continue
            if v == 0:
                ans.append("H")
                h -= 1
                continue
            # paths if we put H now
            ways = math.comb(h + v - 1, v)
            if k <= ways:
                ans.append("H")
                h -= 1
            else:
                ans.append("V")
                k -= ways
                v -= 1
        return "".join(ans)

    def kthSmallestPath_dp(self, destination: List[int], k: int) -> str:
        """
        Interview explanation:
        Alternate: precompute C via DP table then same greedy decisions.

        Algorithm (DP combos + greedy):
        - Build Pascal triangle for combinations; same H/V selection.

        Complexity: O((h+v)^2) precompute + O(h+v).
        """
        row, col = destination
        N = row + col
        C = [[0] * (N + 1) for _ in range(N + 1)]
        for i in range(N + 1):
            C[i][0] = 1
            for j in range(1, i + 1):
                C[i][j] = C[i - 1][j - 1] + C[i - 1][j]
        v, h = row, col
        ans = []
        for _ in range(N):
            if h == 0:
                ans.append("V")
                v -= 1
            elif v == 0:
                ans.append("H")
                h -= 1
            else:
                ways = C[h + v - 1][v]
                if k <= ways:
                    ans.append("H")
                    h -= 1
                else:
                    ans.append("V")
                    k -= ways
                    v -= 1
        return "".join(ans)
# @lc code=end
