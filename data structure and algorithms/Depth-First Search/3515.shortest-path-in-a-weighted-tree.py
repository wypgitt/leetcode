#
# @lc app=leetcode id=3515 lang=python3
#
# [3515] Shortest Path in a Weighted Tree
#
# https://leetcode.com/problems/shortest-path-in-a-weighted-tree/description/
#
# algorithms
# Hard (41.53%)
# Likes:    67
# Dislikes: 2
# Total Accepted:    7.6K
# Total Submissions: 18.3K
# Testcase Example:  "2\n[[1,2,7]]\n[[2,2],[1,1,2,4],[2,2]]"
#
#
# You are given an integer n and an undirected, weighted tree rooted at
# node 1 with n nodes numbered from 1 to n. This is represented by a 2D
# array edges of length n - 1, where edges[i] = [u_i, v_i, w_i] indicates
# an undirected edge from node u_i to v_i with weight w_i.
#
# You are also given a 2D integer array queries of length q, where each
# queries[i] is either:
#
# [1, u, v, w'] – Update the weight of the edge between nodes u and v to
# w', where (u, v) is guaranteed to be an edge present in edges.
#
# [2, x] – Compute the shortest path distance from the root node 1 to node
# x.
#
# Return an integer array answer, where answer[i] is the shortest path
# distance from node 1 to x for the i^th query of [2, x].
#
# Example 1:
#
# Input: n = 2, edges = [[1,2,7]], queries = [[2,2],[1,1,2,4],[2,2]]
#
# Output: [7,4]
#
# Explanation:
#
# Query [2,2]: The shortest path from root node 1 to node 2 is 7.
#
# Query [1,1,2,4]: The weight of edge (1,2) changes from 7 to 4.
#
# Query [2,2]: The shortest path from root node 1 to node 2 is 4.
#
# Example 2:
#
# Input: n = 3, edges = [[1,2,2],[1,3,4]], queries =
# [[2,1],[2,3],[1,1,3,7],[2,2],[2,3]]
#
# Output: [0,4,2,7]
#
# Explanation:
#
# Query [2,1]: The shortest path from root node 1 to node 1 is 0.
#
# Query [2,3]: The shortest path from root node 1 to node 3 is 4.
#
# Query [1,1,3,7]: The weight of edge (1,3) changes from 4 to 7.
#
# Query [2,2]: The shortest path from root node 1 to node 2 is 2.
#
# Query [2,3]: The shortest path from root node 1 to node 3 is 7.
#
# Example 3:
#
# Input: n = 4, edges = [[1,2,2],[2,3,1],[3,4,5]], queries =
# [[2,4],[2,3],[1,2,3,3],[2,2],[2,3]]
#
# Output: [8,3,2,5]
#
# Explanation:
#
# Query [2,4]: The shortest path from root node 1 to node 4 consists of
# edges (1,2), (2,3), and (3,4) with weights 2 + 1 + 5 = 8.
#
# Query [2,3]: The shortest path from root node 1 to node 3 consists of
# edges (1,2) and (2,3) with weights 2 + 1 = 3.
#
# Query [1,2,3,3]: The weight of edge (2,3) changes from 1 to 3.
#
# Query [2,2]: The shortest path from root node 1 to node 2 is 2.
#
# Query [2,3]: The shortest path from root node 1 to node 3 consists of
# edges (1,2) and (2,3) with updated weights 2 + 3 = 5.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i] == [u_i, v_i, w_i]
#
# 1 <= u_i, v_i <= n
#
# 1 <= w_i <= 10^4
#
# The input is generated such that edges represents a valid tree.
#
# 1 <= queries.length == q <= 10^5
#
# queries[i].length == 2 or 4
#
# queries[i] == [1, u, v, w'] or,
#
# queries[i] == [2, x]
#
# 1 <= u, v, x <= n
#
# (u, v) is always an edge from edges.
#
# 1 <= w' <= 10^4
#

# @lc code=start
from typing import List


class BIT:
    """Fenwick tree supporting range add / point query."""

    def __init__(self, n: int):
        self.n = n
        self.bit = [0] * (n + 2)

    def _add(self, i: int, v: int) -> None:
        i += 1
        while i <= self.n + 1:
            self.bit[i] += v
            i += i & -i

    def range_add(self, l: int, r: int, v: int) -> None:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        if l > r:
            return
        self._add(l, v)
        self._add(r + 1, -v)

    def query(self, i: int) -> int:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        i += 1
        s = 0
        while i > 0:
            s += self.bit[i]
            i -= i & -i
        return s


class Solution:
    def treeQueries(
        self, n: int, edges: List[List[int]], queries: List[List[int]]
    ) -> List[int]:
        """
        Interview explanation:
        Tree distances from root 1; edge-weight updates change an entire subtree.
        Euler tour + Fenwick range-add / point-query keeps dist[x] updatable in
        log n.

        Algorithm:
        - Build tree; DFS for parent, in/out times, initial distances.
        - Init BIT with dist[in[u]] at each node.
        - Type 1: delta on child's [in, out]; type 2: query BIT at in[x].

        Complexity: O((n + q) log n) time, O(n) space.
        """
        g = [[] for _ in range(n + 1)]
        weight = {}
        for u, v, w in edges:
            g[u].append(v)
            g[v].append(u)
            weight[(min(u, v), max(u, v))] = w

        tin = [0] * (n + 1)
        tout = [0] * (n + 1)
        dist = [0] * (n + 1)
        parent = [0] * (n + 1)
        time = 0

        def dfs(u: int, p: int) -> None:
            nonlocal time
            tin[u] = time
            time += 1
            for v in g[u]:
                if v == p:
                    continue
                parent[v] = u
                dist[v] = dist[u] + weight[(min(u, v), max(u, v))]
                dfs(v, u)
            tout[u] = time - 1

        dfs(1, 0)
        bit = BIT(n)
        for u in range(1, n + 1):
            bit.range_add(tin[u], tin[u], dist[u])

        ans = []
        for q in queries:
            if q[0] == 1:
                _, u, v, w2 = q
                key = (min(u, v), max(u, v))
                old = weight[key]
                delta = w2 - old
                weight[key] = w2
                child = v if parent[v] == u else u
                bit.range_add(tin[child], tout[child], delta)
            else:
                ans.append(bit.query(tin[q[1]]))
        return ans
# @lc code=end

