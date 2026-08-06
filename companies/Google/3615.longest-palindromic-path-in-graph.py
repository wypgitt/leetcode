#
# @lc app=leetcode id=3615 lang=python3
#
# [3615] Longest Palindromic Path in Graph
#
# https://leetcode.com/problems/longest-palindromic-path-in-graph/description/
#
# algorithms
# Hard (22.31%)
# Likes:    60
# Dislikes: 5
# Total Accepted:    7.8K
# Total Submissions: 35K
# Testcase Example:  "3\n[[0,1],[1,2]]\n\"aba\""
#
#
# You are given an integer n and an undirected graph with n nodes labeled
# from 0 to n - 1 and a 2D array edges, where edges[i] = [u_i, v_i]
# indicates an edge between nodes u_i and v_i.
#
# You are also given a string label of length n, where label[i] is the
# character associated with node i.
#
# You may start at any node and move to any adjacent node, visiting each
# node at most once.
#
# Return the maximum possible length of a palindrome that can be formed by
# visiting a set of unique nodes along a valid path.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[1,2]], label = "aba"
#
# Output: 3
#
# Explanation:
#
# The longest palindromic path is from node 0 to node 2 via node 1,
# following the path 0 → 1 → 2 forming string "aba".
#
# This is a valid palindrome of length 3.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1],[0,2]], label = "abc"
#
# Output: 1
#
# Explanation:
#
# No path with more than one node forms a palindrome.
#
# The best option is any single node, giving a palindrome of length 1.
#
# Example 3:
#
# Input: n = 4, edges = [[0,2],[0,3],[3,1]], label = "bbac"
#
# Output: 3
#
# Explanation:
#
# The longest palindromic path is from node 0 to node 1, following the
# path 0 → 3 → 1, forming string "bcb".
#
# This is a valid palindrome of length 3.
#
# Constraints:
#
# 1 <= n <= 14
#
# n - 1 <= edges.length <= n * (n - 1) / 2
#
# edges[i] == [u_i, v_i]
#
# 0 <= u_i, v_i <= n - 1
#
# u_i != v_i
#
# label.length == n
#
# label consists of lowercase English letters.
#
# There are no duplicate edges.
#

# @lc code=start

from functools import cache
from typing import List


class Solution:
    def maxLen(self, n: int, edges: List[List[int]], label: str) -> int:
        """
        Interview explanation:
        Longest simple path whose labels form a palindrome. n ≤ 14 → bitmask DP
        expanding a palindrome from the center outward.

        Algorithm:
        - dp(i, j, mask): max extra length expandable from ends i,j with used mask.
        - Seed odd centers (i,i) and even centers (edge with equal labels).
        - Expand by matching-label unused neighbors of both ends.

        Complexity: O(n^2 · 2^n · deg^2) time, O(n^2 · 2^n) space.
        """
        g: List[List[int]] = [[] for _ in range(n)]
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)

        @cache
        def dp(i: int, j: int, mask: int) -> int:
            if i > j:
                return dp(j, i, mask)
            best = 0
            for a in g[i]:
                if mask & (1 << a):
                    continue
                for b in g[j]:
                    if a == b or (mask & (1 << b)) or label[a] != label[b]:
                        continue
                    best = max(best, dp(a, b, mask | (1 << a) | (1 << b)) + 2)
            return best

        ans = 0
        for i in range(n):
            ans = max(ans, dp(i, i, 1 << i) + 1)
        for a, b in edges:
            if label[a] == label[b]:
                ans = max(ans, dp(a, b, (1 << a) | (1 << b)) + 2)
        return ans
# @lc code=end
