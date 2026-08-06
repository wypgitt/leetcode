#
# @lc app=leetcode id=1786 lang=python3
#
# [1786] Number of Restricted Paths From First to Last Node
#
# https://leetcode.com/problems/number-of-restricted-paths-from-first-to-last-node/description/
#
# algorithms
# Medium (41.64%)
# Likes:    1217
# Dislikes: 236
# Total Accepted:    36.9K
# Total Submissions: 88.7K
# Testcase Example:  "5"
#
# There is an undirected weighted connected graph. You are given a positive
# integer n which denotes that the graph has n nodes labeled from 1 to n, and
# an array edges where each edges[i] = [u_i, v_i, weight_i] denotes that there
# is an edge between nodes u_i and v_i with weight equal to weight_i.
#
# A path from node start to node end is a sequence of nodes [z_0, z_1,_ z_2,
# ..., z_k] such that z_0 = start and z_k = end and there is an edge between
# z_i and z_i+1 where 0 <= i <= k-1.
#
# The distance of a path is the sum of the weights on the edges of the path.
# Let distanceToLastNode(x) denote the shortest distance of a path between node
# n and node x. A restricted path is a path that also satisfies that
# distanceToLastNode(z_i) > distanceToLastNode(z_i+1) where 0 <= i <= k-1.
#
# Return the number of restricted paths from node 1 to node n. Since that
# number may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 5, edges =
# [[1,2,3],[1,3,3],[2,3,1],[1,4,2],[5,2,2],[3,5,1],[5,4,10]]
# Output: 3
# Explanation: Each circle contains the node number in black and its
# distanceToLastNode value in blue. The three restricted paths are:
# 1) 1 --> 2 --> 5
# 2) 1 --> 2 --> 3 --> 5
# 3) 1 --> 3 --> 5
#
# Example 2:
#
# Input: n = 7, edges =
# [[1,3,1],[4,1,2],[7,3,4],[2,5,3],[5,6,1],[6,7,2],[7,5,3],[2,6,4]]
# Output: 1
# Explanation: Each circle contains the node number in black and its
# distanceToLastNode value in blue. The only restricted path is 1 --> 3 --> 7.
#
# Constraints:
#
# 1 <= n <= 2 * 10^4
#
# n - 1 <= edges.length <= 4 * 10^4
#
# edges[i].length == 3
#
# 1 <= u_i, v_i <= n
#
# u_i != v_i
#
# 1 <= weight_i <= 10^5
#
# There is at most one edge between any two nodes.
#
# There is at least one path between any two nodes.
#

# @lc code=start
from typing import List
import heapq
from functools import lru_cache


class Solution:
    def countRestrictedPaths(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Restricted path: distances-to-n strictly decrease along the path
        (dist[u] > dist[v] for each edge u→v). Dijkstra dist from n; then DP
        count paths from 1 to n where neighbors have smaller dist.

        Algorithm:
        - Dijkstra from n → dist[].
        - dp[u] = sum dp[v] for neighbors v with dist[u] > dist[v]; dp[n]=1.
        - Memoized DFS from 1 (or process nodes by decreasing dist).

        Complexity: O(E log V) Dijkstra + O(E) DP.
        """
        MOD = 10**9 + 7
        g = [[] for _ in range(n + 1)]
        for u, v, w in edges:
            g[u].append((v, w))
            g[v].append((u, w))
        dist = [float("inf")] * (n + 1)
        dist[n] = 0
        pq = [(0, n)]
        while pq:
            d, u = heapq.heappop(pq)
            if d != dist[u]:
                continue
            for v, w in g[u]:
                if dist[v] > d + w:
                    dist[v] = d + w
                    heapq.heappush(pq, (dist[v], v))

        @lru_cache(None)
        def dfs(u: int) -> int:
            if u == n:
                return 1
            total = 0
            for v, _ in g[u]:
                if dist[u] > dist[v]:
                    total = (total + dfs(v)) % MOD
            return total

        return dfs(1)

    def countRestrictedPaths_iter(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate classic: after Dijkstra distances from n, process nodes in
        increasing dist order (topo of the DAG of decreasing-dist edges) and
        accumulate path counts upward to node 1.

        Algorithm:
        - Dijkstra dist from n; dp[n]=1.
        - For u in nodes sorted by dist ascending: for neighbor v with
          dist[v] > dist[u]: dp[v] = (dp[v] + dp[u]) % MOD.
        - return dp[1]

        Complexity: O(E log V) + O(V log V + E).
        """
        # Fix annotation: edges is List[List[int]]
        MOD = 10**9 + 7
        g = [[] for _ in range(n + 1)]
        for u, v, w in edges:
            g[u].append((v, w))
            g[v].append((u, w))
        dist = [float("inf")] * (n + 1)
        dist[n] = 0
        pq = [(0, n)]
        while pq:
            d, u = heapq.heappop(pq)
            if d != dist[u]:
                continue
            for v, w in g[u]:
                if dist[v] > d + w:
                    dist[v] = d + w
                    heapq.heappush(pq, (dist[v], v))
        order = sorted(range(1, n + 1), key=lambda x: dist[x])
        dp = [0] * (n + 1)
        dp[n] = 1
        for u in order:
            for v, _ in g[u]:
                if dist[v] > dist[u]:
                    dp[v] = (dp[v] + dp[u]) % MOD
        return dp[1]
# @lc code=end
