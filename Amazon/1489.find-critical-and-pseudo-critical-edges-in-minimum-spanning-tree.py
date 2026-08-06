#
# @lc app=leetcode id=1489 lang=python3
#
# [1489] Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree
#
# https://leetcode.com/problems/find-critical-and-pseudo-critical-edges-in-minimum-spanning-tree/description/
#
# algorithms
# Hard (66.7%)
# Likes:    2054
# Dislikes: 173
# Total Accepted:    78.1K
# Total Submissions: 117K
# Testcase Example:  "5"
#
# Given a weighted undirected connected graph with n vertices numbered from 0
# to n - 1, and an array edges where edges[i] = [a_i, b_i, weight_i] represents
# a bidirectional and weighted edge between nodes a_i and b_i. A minimum
# spanning tree (MST) is a subset of the graph's edges that connects all
# vertices without cycles and with the minimum possible total edge weight.
#
# Find all the critical and pseudo-critical edges in the given graph's minimum
# spanning tree (MST). An MST edge whose deletion from the graph would cause
# the MST weight to increase is called a critical edge. On the other hand, a
# pseudo-critical edge is that which can appear in some MSTs but not all.
#
# Note that you can return the indices of the edges in any order.
#
# Example 1:
#
# Input: n = 5, edges =
# [[0,1,1],[1,2,1],[2,3,2],[0,3,2],[0,4,3],[3,4,3],[1,4,6]]
# Output: [[0,1],[2,3,4,5]]
# Explanation: The figure above describes the graph.
# The following figure shows all the possible MSTs:
#
# Notice that the two edges 0 and 1 appear in all MSTs, therefore they are
# critical edges, so we return them in the first list of the output.
# The edges 2, 3, 4, and 5 are only part of some MSTs, therefore they are
# considered pseudo-critical edges. We add them to the second list of the
# output.
#
# Example 2:
#
# Input: n = 4, edges = [[0,1,1],[1,2,1],[2,3,1],[0,3,1]]
# Output: [[],[0,1,2,3]]
# Explanation: We can observe that since all 4 edges have equal weight,
# choosing any 3 edges from the given 4 will yield an MST. Therefore all 4
# edges are pseudo-critical.
#
# Constraints:
#
# 2 <= n <= 100
#
# 1 <= edges.length <= min(200, n * (n - 1) / 2)
#
# edges[i].length == 3
#
# 0 <= a_i < b_i < n
#
# 1 <= weight_i <= 1000
#
# All pairs (a_i, b_i) are distinct.
#

# @lc code=start
from typing import List


class Solution:
    def findCriticalAndPseudoCriticalEdges(
        self, n: int, edges: List[List[int]]
    ) -> List[List[int]]:
        """
        Interview explanation:
        Classify MST edges: critical = in all MSTs; pseudo-critical = in some
        but not all. Kruskal with Union-Find: compute MST weight W; edge is
        critical if forcing exclude raises weight / disconnects; pseudo if
        forcing include still achieves W and not critical.

        Algorithm:
        - Annotate edges with index; sort by weight.
        - mst(force_include=None, force_exclude=None) via UF.
        - For each edge: if mst(exclude=i) > W → critical; elif mst(include=i)==W
          → pseudo.

        Complexity: O(E^2 α(n)) time, O(n) space.
        """

        class UF:
            def __init__(self, n):
                self.p = list(range(n))
                self.r = [0] * n
                self.comp = n

            def find(self, x):
                while self.p[x] != x:
                    self.p[x] = self.p[self.p[x]]
                    x = self.p[x]
                return x

            def union(self, a, b):
                ra, rb = self.find(a), self.find(b)
                if ra == rb:
                    return False
                if self.r[ra] < self.r[rb]:
                    ra, rb = rb, ra
                self.p[rb] = ra
                if self.r[ra] == self.r[rb]:
                    self.r[ra] += 1
                self.comp -= 1
                return True

        m = len(edges)
        indexed = [(w, a, b, i) for i, (a, b, w) in enumerate(edges)]
        indexed.sort()

        def mst(include_oi=None, exclude_oi=None):
            uf = UF(n)
            weight = 0
            if include_oi is not None:
                a, b, w = edges[include_oi]
                uf.union(a, b)
                weight += w
            for w, a, b, oi in indexed:
                if exclude_oi is not None and oi == exclude_oi:
                    continue
                if include_oi is not None and oi == include_oi:
                    continue
                if uf.union(a, b):
                    weight += w
            return weight if uf.comp == 1 else float("inf")

        base = mst()
        critical, pseudo = [], []
        for i in range(m):
            if mst(exclude_oi=i) > base:
                critical.append(i)
            elif mst(include_oi=i) == base:
                pseudo.append(i)
        return [critical, pseudo]
# @lc code=end
