#
# @lc app=leetcode id=3585 lang=python3
#
# [3585] Find Weighted Median Node in Tree
#
# https://leetcode.com/problems/find-weighted-median-node-in-tree/description/
#
# algorithms
# Hard (26.38%)
# Likes:    73
# Dislikes: 6
# Total Accepted:    4.8K
# Total Submissions: 18.3K
# Testcase Example:  "2\n[[0,1,7]]\n[[1,0],[0,1]]"
#
#
# You are given an integer n and an undirected, weighted tree rooted at
# node 0 with n nodes numbered from 0 to n - 1. This is represented by a
# 2D array edges of length n - 1, where edges[i] = [u_i, v_i, w_i]
# indicates an edge from node u_i to v_i with weight w_i.
#
# The weighted median node is defined as the first node x on the path from
# u_i to v_i such that the sum of edge weights from u_i to x is greater
# than or equal to half of the total path weight.
#
# You are given a 2D integer array queries. For each queries[j] = [u_j,
# v_j], determine the weighted median node along the path from u_j to v_j.
#
# Return an array ans, where ans[j] is the node index of the weighted
# median for queries[j].
#
# Example 1:
#
# Input: n = 2, edges = [[0,1,7]], queries = [[1,0],[0,1]]
#
# Output: [0,1]
#
# Explanation:
#
#                         Query
#                         Path
#                         Edge
#
#                         Weights
#                         Total
#
#                         Path
#
#                         Weight
#                         Half
#                         Explanation
#                         Answer
#
#                         [1, 0]
#                         1 → 0
#                         [7]
#                         7
#                         3.5
#                         Sum from 1 → 0 = 7 >= 3.5, median is node 0.
#                         0
#
#                         [0, 1]
#                         0 → 1
#                         [7]
#                         7
#                         3.5
#                         Sum from 0 → 1 = 7 >= 3.5, median is node 1.
#                         1
#
# Example 2:
#
# Input: n = 3, edges = [[0,1,2],[2,0,4]], queries = [[0,1],[2,0],[1,2]]
#
# Output: [1,0,2]
#
# Explanation:
#
#                         Query
#                         Path
#                         Edge
#
#                         Weights
#                         Total
#
#                         Path
#
#                         Weight
#                         Half
#                         Explanation
#                         Answer
#
#                         [0, 1]
#                         0 → 1
#                         [2]
#                         2
#                         1
#                         Sum from 0 → 1 = 2 >= 1, median is node 1.
#                         1
#
#                         [2, 0]
#                         2 → 0
#                         [4]
#                         4
#                         2
#                         Sum from 2 → 0 = 4 >= 2, median is node 0.
#                         0
#
#                         [1, 2]
#                         1 → 0 → 2
#                         [2, 4]
#                         6
#                         3
#                         Sum from 1 → 0 = 2 < 3.
#
#                         Sum from 1 → 2 = 2 + 4 = 6 >= 3, median is node
# 2.
#                         2
#
# Example 3:
#
# Input: n = 5, edges = [[0,1,2],[0,2,5],[1,3,1],[2,4,3]], queries =
# [[3,4],[1,2]]
#
# Output: [2,2]
#
# Explanation:
#
#                         Query
#                         Path
#                         Edge
#
#                         Weights
#                         Total
#
#                         Path
#
#                         Weight
#                         Half
#                         Explanation
#                         Answer
#
#                         [3, 4]
#                         3 → 1 → 0 → 2 → 4
#                         [1, 2, 5, 3]
#                         11
#                         5.5
#                         Sum from 3 → 1 = 1 < 5.5.
#
#                         Sum from 3 → 0 = 1 + 2 = 3 < 5.5.
#
#                         Sum from 3 → 2 = 1 + 2 + 5 = 8 >= 5.5, median is
# node 2.
#                         2
#
#                         [1, 2]
#                         1 → 0 → 2
#                         [2, 5]
#                         7
#                         3.5
#
# Sum from 1 → 0 = 2 < 3.5.
#
#                         Sum from 1 → 2 = 2 + 5 = 7 >= 3.5, median is
# node 2.
#
#                         2
#
# Constraints:
#
# 2 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i] == [u_i, v_i, w_i]
#
# 0 <= u_i, v_i < n
#
# 1 <= w_i <= 10^9
#
# 1 <= queries.length <= 10^5
#
# queries[j] == [u_j, v_j]
#
# 0 <= u_j, v_j < n
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start

import sys
from typing import List

sys.setrecursionlimit(200000)


class Solution:
    def findMedian(
        self, n: int, edges: List[List[int]], queries: List[List[int]]
    ) -> List[int]:
        """
        Interview explanation:
        Weighted median on u→v is the first node x with 2*weight(u,x) ≥ total.
        Binary lifting gives LCA, distances, and k-step jumps for binary search
        on the hop count along the path.

        Algorithm:
        - Root at 0; build parent/depth/dist and 2^k up-jumps.
        - For query (u,v): tot = dist(u,v); bisect hops k on path u→v until
          weight(u, jump(k)) * 2 ≥ tot; map k across the LCA bend.

        Complexity: O((n+q) log n) time, O(n log n) space.
        """
        g: List[List[tuple[int, int]]] = [[] for _ in range(n)]
        for u, v, w in edges:
            g[u].append((v, w))
            g[v].append((u, w))

        LOG = n.bit_length()
        parent = [[-1] * n for _ in range(LOG)]
        depth = [0] * n
        dist = [0] * n

        def dfs(u: int, p: int) -> None:
            parent[0][u] = p
            for v, w in g[u]:
                if v == p:
                    continue
                depth[v] = depth[u] + 1
                dist[v] = dist[u] + w
                dfs(v, u)

        dfs(0, -1)
        for k in range(1, LOG):
            for i in range(n):
                mid = parent[k - 1][i]
                if mid != -1:
                    parent[k][i] = parent[k - 1][mid]

        def jump(u: int, k: int) -> int:
            bit = 0
            while k:
                if k & 1:
                    u = parent[bit][u]
                    if u == -1:
                        return -1
                k >>= 1
                bit += 1
            return u

        def lca(u: int, v: int) -> int:
            if depth[u] < depth[v]:
                u, v = v, u
            u = jump(u, depth[u] - depth[v])
            if u == v:
                return u
            for k in range(LOG - 1, -1, -1):
                if parent[k][u] != parent[k][v]:
                    u = parent[k][u]
                    v = parent[k][v]
            return parent[0][u]

        def path_dist(u: int, v: int) -> int:
            a = lca(u, v)
            return dist[u] + dist[v] - 2 * dist[a]

        ans = []
        for u, v in queries:
            a = lca(u, v)
            tot = path_dist(u, v)
            up = depth[u] - depth[a]
            down = depth[v] - depth[a]

            def weight_after(k: int) -> tuple[int, int]:
                if k <= up:
                    t = jump(u, k)
                else:
                    need = down - (k - up)
                    t = jump(v, need)
                return path_dist(u, t), t

            lo, hi = 0, up + down
            while lo < hi:
                mid = (lo + hi) // 2
                if weight_after(mid)[0] * 2 < tot:
                    lo = mid + 1
                else:
                    hi = mid
            ans.append(weight_after(lo)[1])
        return ans
# @lc code=end
