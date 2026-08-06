#
# @lc app=leetcode id=3887 lang=python3
#
# [3887] Incremental Even-Weighted Cycle Queries
#
# https://leetcode.com/problems/incremental-even-weighted-cycle-queries/description/
#
# algorithms
# Hard (51.99%)
# Likes:    79
# Dislikes: 4
# Total Accepted:    8.2K
# Total Submissions: 15.8K
# Testcase Example:  "3\n[[0,1,1],[1,2,1],[0,2,1]]"
#
#
# You are given a positive integer n.
#
# There is an undirected graph with n nodes labeled from 0 to n - 1.
# Initially, the graph has no edges.
#
# You are also given a 2D integer array edges, where edges[i] = [u_i, v_i,
# w_i] represents an edge between nodes u_i and v_i with weight w_i. The
# weight w_i is either 0 or 1.
#
# Process the edges in edges in the given order. For each edge, add it to
# the graph only if, after adding it, the sum of the weights of the edges
# in every cycle in the resulting graph is even.
#
# Return an integer denoting the number of edges that are successfully
# added to the graph.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1,1],[1,2,1],[0,2,1]]
#
# Output: 2
#
# Explanation:
#
# [0, 1, 1]: We add the edge between vertex 0 and vertex 1 with weight 1.
#
# [1, 2, 1]: We add the edge between vertex 1 and vertex 2 with weight 1.
#
# [0, 2, 1]: The edge between vertex 0 and vertex 2 (the dashed edge in
# the diagram) is not added because the cycle 0 - 1 - 2 - 0 has total edge
# weight 1 + 1 + 1 = 3, which is an odd number.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1,1],[1,2,1],[0,2,0]]
#
# Output: 3
#
# Explanation:
#
# [0, 1, 1]: We add the edge between vertex 0 and vertex 1 with weight 1.
#
# [1, 2, 1]: We add the edge between vertex 1 and vertex 2 with weight 1.
#
# [0, 2, 0]: We add the edge between vertex 0 and vertex 2 with weight 0.
#
# Note that the cycle 0 - 1 - 2 - 0 has total edge weight 1 + 1 + 0 = 2,
# which is an even number.
#
# Constraints:
#
# 3 <= n <= 5 * 10^4
#
# 1 <= edges.length <= 5 * 10^4
#
# edges[i] = [u_i, v_i, w_i]
#
# 0 <= u_i < v_i < n
#
# All edges are distinct.
#
# w_i = 0 or w_i = 1
#

# @lc code=start
from typing import List


class Solution:
    def numberOfEdgesAdded(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Every cycle weight sum even ⇔ XOR of cycle edges is 0. Maintain a
        bipartition / XOR potential via DSU with parity to roots.

        Algorithm:
        - find returns root and compresses XOR-to-root parity.
        - Different components: always union; set parent XOR so potentials match w.
        - Same component: add iff parity[u] XOR parity[v] XOR w == 0.

        Complexity: O((n + m) α(n)) time, O(n) space.
        """
        parent = list(range(n))
        rank = [0] * n
        parity = [0] * n

        def find(x: int) -> int:
            stk = []
            while parent[x] != x:
                stk.append(x)
                x = parent[x]
            prev = parity[x]
            while stk:
                y = stk.pop()
                parity[y] ^= prev
                prev = parity[y]
                parent[y] = x
            return x

        def union(u: int, v: int, w: int) -> bool:
            u0, v0 = u, v
            ru, rv = find(u), find(v)
            if ru == rv:
                return (parity[u0] ^ w ^ parity[v0]) == 0
            if rank[ru] > rank[rv]:
                ru, rv = rv, ru
            elif rank[ru] == rank[rv]:
                rank[rv] += 1
            parent[ru] = rv
            parity[ru] = parity[u0] ^ w ^ parity[v0]
            return True

        return sum(union(u, v, w) for u, v, w in edges)
# @lc code=end
