#
# @lc app=leetcode id=684 lang=python3
#
# [684] Redundant Connection
#
# https://leetcode.com/problems/redundant-connection/description/
#
# algorithms
# Medium (68.02%)
# Likes:    7257
# Dislikes: 452
# Total Accepted:    683K
# Total Submissions: 1.0M
# Testcase Example:  "[[1,2],[1,3],[2,3]]"
#
# In this problem, a tree is an undirected graph that is connected and has no
# cycles.
#
# You are given a graph that started as a tree with n nodes labeled from 1 to
# n, with one additional edge added. The added edge has two different vertices
# chosen from 1 to n, and was not an edge that already existed. The graph is
# represented as an array edges of length n where edges[i] = [a_i, b_i]
# indicates that there is an edge between nodes a_i and b_i in the graph.
#
# Return an edge that can be removed so that the resulting graph is a tree of n
# nodes. If there are multiple answers, return the answer that occurs last in
# the input.
#
# Example 1:
#
# Input: edges = [[1,2],[1,3],[2,3]]
# Output: [2,3]
#
# Example 2:
#
# Input: edges = [[1,2],[2,3],[3,4],[1,4],[1,5]]
# Output: [1,4]
#
# Constraints:
#
# n == edges.length
#
# 3 <= n <= 1000
#
# edges[i].length == 2
#
# 1 <= a_i < b_i <= edges.length
#
# a_i != b_i
#
# There are no repeated edges.
#
# The given graph is connected.
#

# @lc code=start
from typing import List


class Solution:
    def findRedundantConnection(self, edges: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Undirected graph that was a tree plus one extra edge. Union-Find: the
        first edge whose endpoints are already connected is the redundant one
        (last such in input order — process in order, return when union fails).

        Algorithm:
        - parent/rank DSU. For each edge, if find(u)==find(v) return it; else union.

        Complexity: O(n α(n)) time, O(n) space.
        """
        n = len(edges)
        parent = list(range(n + 1))
        rank = [0] * (n + 1)

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> bool:
            ra, rb = find(a), find(b)
            if ra == rb:
                return False
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1
            return True

        for u, v in edges:
            if not union(u, v):
                return [u, v]
        return []
# @lc code=end
