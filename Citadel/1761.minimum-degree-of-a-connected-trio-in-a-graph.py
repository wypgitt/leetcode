#
# @lc app=leetcode id=1761 lang=python3
#
# [1761] Minimum Degree of a Connected Trio in a Graph
#
# https://leetcode.com/problems/minimum-degree-of-a-connected-trio-in-a-graph/description/
#
# algorithms
# Hard (44.68%)
# Likes:    363
# Dislikes: 296
# Total Accepted:    30.7K
# Total Submissions: 68.7K
# Testcase Example:  "6"
#
# You are given an undirected graph. You are given an integer n which is the
# number of nodes in the graph and an array edges, where each edges[i] = [u_i,
# v_i] indicates that there is an undirected edge between u_i and v_i.
#
# A connected trio is a set of three nodes where there is an edge between every
# pair of them.
#
# The degree of a connected trio is the number of edges where one endpoint is
# in the trio, and the other is not.
#
# Return the minimum degree of a connected trio in the graph, or -1 if the
# graph has no connected trios.
#
# Example 1:
#
# Input: n = 6, edges = [[1,2],[1,3],[3,2],[4,1],[5,2],[3,6]]
# Output: 3
# Explanation: There is exactly one trio, which is [1,2,3]. The edges that form
# its degree are bolded in the figure above.
#
# Example 2:
#
# Input: n = 7, edges = [[1,3],[4,1],[4,3],[2,5],[5,6],[6,7],[7,5],[2,6]]
# Output: 0
# Explanation: There are exactly three trios:
# 1) [1,4,3] with degree 0.
# 2) [2,5,6] with degree 2.
# 3) [5,6,7] with degree 2.
#
# Constraints:
#
# 2 <= n <= 400
#
# edges[i].length == 2
#
# 1 <= edges.length <= n * (n-1) / 2
#
# 1 <= u_i, v_i <= n
#
# u_i != v_i
#
# There are no repeated edges.
#

# @lc code=start
from typing import List


class Solution:
    def minTrioDegree(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Connected trio = triangle. Trio degree = deg[u]+deg[v]+deg[w]−6
        (subtract the 3 edges' 6 endpoints). Enumerate triangles via adj sets.

        Algorithm:
        - Build adj sets + degrees.
        - For u < v < w with uv,uw,vw: track min(deg sum − 6).

        Complexity: O(n * d^2) with sets / O(E * avg_deg); O(n+E) space.
        """
        deg = [0] * (n + 1)
        adj = [set() for _ in range(n + 1)]
        for u, v in edges:
            adj[u].add(v)
            adj[v].add(u)
            deg[u] += 1
            deg[v] += 1
        ans = float("inf")
        for u in range(1, n + 1):
            for v in adj[u]:
                if v <= u:
                    continue
                for w in adj[u]:
                    if w <= v:
                        continue
                    if w in adj[v]:
                        ans = min(ans, deg[u] + deg[v] + deg[w] - 6)
        return -1 if ans == float("inf") else ans

    def minTrioDegree_matrix(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: boolean adjacency matrix for O(1) edge checks; enumerate
        all candidate triples along edges.

        Algorithm:
        - g[u][v]=True; for u<v with edge, for w>v if g[u][w] and g[v][w]: update.

        Complexity: O(n^3) time, O(n^2) space.
        """
        g = [[False] * (n + 1) for _ in range(n + 1)]
        deg = [0] * (n + 1)
        for u, v in edges:
            g[u][v] = g[v][u] = True
            deg[u] += 1
            deg[v] += 1
        ans = float("inf")
        for u in range(1, n + 1):
            for v in range(u + 1, n + 1):
                if not g[u][v]:
                    continue
                for w in range(v + 1, n + 1):
                    if g[u][w] and g[v][w]:
                        ans = min(ans, deg[u] + deg[v] + deg[w] - 6)
        return -1 if ans == float("inf") else ans
# @lc code=end
