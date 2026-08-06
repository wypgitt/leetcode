#
# @lc app=leetcode id=3613 lang=python3
#
# [3613] Minimize Maximum Component Cost
#
# https://leetcode.com/problems/minimize-maximum-component-cost/description/
#
# algorithms
# Medium (43.79%)
# Likes:    131
# Dislikes: 9
# Total Accepted:    25.4K
# Total Submissions: 58K
# Testcase Example:  "5\n[[0,1,4],[1,2,3],[1,3,2],[3,4,6]]\n2"
#
#
# You are given an undirected connected graph with n nodes labeled from 0
# to n - 1 and a 2D integer array edges where edges[i] = [u_i, v_i, w_i]
# denotes an undirected edge between node u_i and node v_i with weight
# w_i, and an integer k.
#
# You are allowed to remove any number of edges from the graph such that
# the resulting graph has at most k connected components.
#
# The cost of a component is defined as the maximum edge weight in that
# component. If a component has no edges, its cost is 0.
#
# Return the minimum possible value of the maximum cost among all
# components after such removals.
#
# Example 1:
#
# Input: n = 5, edges = [[0,1,4],[1,2,3],[1,3,2],[3,4,6]], k = 2
#
# Output: 4
#
# Explanation:
#
# Remove the edge between nodes 3 and 4 (weight 6).
#
# The resulting components have costs of 0 and 4, so the overall maximum
# cost is 4.
#
# Example 2:
#
# Input: n = 4, edges = [[0,1,5],[1,2,5],[2,3,5]], k = 1
#
# Output: 5
#
# Explanation:
#
# No edge can be removed, since allowing only one component (k = 1)
# requires the graph to stay fully connected.
#
# That single component’s cost equals its largest edge weight, which is 5.
#
# Constraints:
#
# 1 <= n <= 5 * 10^4
#
# 0 <= edges.length <= 10^5
#
# edges[i].length == 3
#
# 0 <= u_i, v_i < n
#
# 1 <= w_i <= 10^6
#
# 1 <= k <= n
#
# The input graph is connected.
#

# @lc code=start

from typing import List


class UnionFind:
    def __init__(self, n: int) -> None:
        """
        Interview explanation:
        Disjoint-set used to build a forest while scanning edges by weight.
        """
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        """
        Interview explanation:
        Path-compressed find of the component root.
        """
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        """
        Interview explanation:
        Union by rank; True if a merge occurred.
        """
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


class Solution:
    def minCost(self, n: int, edges: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Minimize the max edge weight kept while ending with ≤ k components
        (component cost = max edge inside it).

        Algorithm:
        - Kruskal: sort edges ascending; union until merges == n-k.
        - That last edge weight is the minimized bottleneck; 0 if k ≥ n.

        Complexity: O(E log E · α(n)) time, O(n) space.
        """
        edges = sorted(edges, key=lambda e: e[2])
        uf = UnionFind(n)
        merges = 0
        for u, v, w in edges:
            if not uf.union(u, v):
                continue
            merges += 1
            if merges == n - k:
                return w
        return 0
# @lc code=end
