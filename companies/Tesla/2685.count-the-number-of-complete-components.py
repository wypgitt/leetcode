#
# @lc app=leetcode id=2685 lang=python3
#
# [2685] Count the Number of Complete Components
#
# https://leetcode.com/problems/count-the-number-of-complete-components/description/
#
# algorithms
# Medium (80.80%)
# Likes:    1517
# Dislikes: 33
# Total Accepted:    253K
# Total Submissions: 313.1K
# Testcase Example:  "6\n[[0,1],[0,2],[1,2],[3,4]]"
#
# You are given an integer n. There is an undirected graph with n vertices,
# numbered from 0 to n - 1. You are given a 2D integer array edges where
# edges[i] = [a_i, b_i] denotes that there exists an undirected edge connecting
# vertices a_i and b_i.
#
# Return the number of complete connected components of the graph.
#
# A connected component is a subgraph of a graph in which there exists a path
# between any two vertices, and no vertex of the subgraph shares an edge with a
# vertex outside of the subgraph.
#
# A connected component is said to be complete if there exists an edge between
# every pair of its vertices.
#
#
#
# Example 1:
#
# Input: n = 6, edges = [[0,1],[0,2],[1,2],[3,4]]
# Output: 3
# Explanation: From the picture above, one can see that all of the components of
# this graph are complete.
#
# Example 2:
#
# Input: n = 6, edges = [[0,1],[0,2],[1,2],[3,4],[3,5]]
# Output: 1
# Explanation: The component containing vertices 0, 1, and 2 is complete since
# there is an edge between every pair of two vertices. On the other hand, the
# component containing vertices 3, 4, and 5 is not complete since there is no
# edge between vertices 4 and 5. Thus, the number of complete components in this
# graph is 1.
#
#
#
# Constraints:
#
#
# 1 <= n <= 50
#
#
# 0 <= edges.length <= n * (n - 1) / 2
#
#
# edges[i].length == 2
#
#
# 0 <= a_i, b_i <= n - 1
#
#
# a_i != b_i
#
#
# There are no repeated edges.
#

# @lc code=start

from typing import List
from collections import defaultdict


class Solution:
    def countCompleteComponents(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Undirected graph; a connected component is complete if every pair is edged (clique).
        Count complete components.

        Algorithm:
        - DFS/BFS each component; count nodes v and edges e; complete iff e == v*(v-1)/2.

        Complexity: O(n + m) time, O(n + m) space.
        """
        g = defaultdict(list)
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        seen = [False] * n
        ans = 0

        def dfs(u: int, nodes: List[int]) -> None:
            seen[u] = True
            nodes.append(u)
            for v in g[u]:
                if not seen[v]:
                    dfs(v, nodes)

        for i in range(n):
            if seen[i]:
                continue
            nodes: List[int] = []
            dfs(i, nodes)
            v = len(nodes)
            e = sum(len(g[u]) for u in nodes) // 2
            if e == v * (v - 1) // 2:
                ans += 1
        return ans

    def countCompleteComponents_uf(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate Union-Find: union edges; per component count nodes and edges; check clique.

        Algorithm:
        - UF parents; tally size and edge counts; count components with e == v*(v-1)/2.

        Complexity: O(n + m α(n)) time, O(n) space.
        """
        parent = list(range(n))
        size = [1] * n

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if size[ra] < size[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            size[ra] += size[rb]

        for a, b in edges:
            union(a, b)
        edge_cnt = [0] * n
        for a, b in edges:
            edge_cnt[find(a)] += 1
        ans = 0
        seen = set()
        for i in range(n):
            r = find(i)
            if r in seen:
                continue
            seen.add(r)
            v = size[r]
            if edge_cnt[r] == v * (v - 1) // 2:
                ans += 1
        return ans
# @lc code=end
