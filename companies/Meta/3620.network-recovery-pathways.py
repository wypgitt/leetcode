#
# @lc app=leetcode id=3620 lang=python3
#
# [3620] Network Recovery Pathways
#
# https://leetcode.com/problems/network-recovery-pathways/description/
#
# algorithms
# Hard (50.71%)
# Likes:    455
# Dislikes: 27
# Total Accepted:    87.7K
# Total Submissions: 173K
# Testcase Example:  "[[0,1,5],[1,3,10],[0,2,3],[2,3,4]]\n[true,true,true,true]\n10"
#
#
# You are given a directed acyclic graph of n nodes numbered from
# 0 to n − 1. This is represented by a 2D array edges of length m, where
# edges[i] = [u_i, v_i, cost_i] indicates a one‑way communication from
# node u_i to node v_i with a recovery cost of cost_i.
#
# Some nodes may be offline. You are given a boolean array online where
# online[i] = true means node i is online. Nodes 0 and n − 1 are always
# online.
#
# A path from 0 to n − 1 is valid if:
#
# All intermediate nodes on the path are online.
#
# The total recovery cost of all edges on the path does not exceed k.
#
# For each valid path, define its score as the minimum edge‑cost along
# that path.
#
# Return the maximum path score (i.e., the largest minimum-edge cost)
# among all valid paths. If no valid path exists, return -1.
#
# Example 1:
#
# Input: edges = [[0,1,5],[1,3,10],[0,2,3],[2,3,4]], online =
# [true,true,true,true], k = 10
#
# Output: 3
#
# Explanation:
#
# The graph has two possible routes from node 0 to node 3:
#
# Path 0 → 1 → 3
#
# Total cost = 5 + 10 = 15, which exceeds k (15 > 10), so this path is
# invalid.
#
# Path 0 → 2 → 3
#
# Total cost = 3 + 4 = 7 <= k, so this path is valid.
#
# The minimum edge‐cost along this path is min(3, 4) = 3.
#
# There are no other valid paths. Hence, the maximum among all valid
# path‐scores is 3.
#
# Example 2:
#
# Input: edges = [[0,1,7],[1,4,5],[0,2,6],[2,3,6],[3,4,2],[2,4,6]], online
# = [true,true,true,false,true], k = 12
#
# Output: 6
#
# Explanation:
#
# Node 3 is offline, so any path passing through 3 is invalid.
#
# Consider the remaining routes from 0 to 4:
#
# Path 0 → 1 → 4
#
# Total cost = 7 + 5 = 12 <= k, so this path is valid.
#
# The minimum edge‐cost along this path is min(7, 5) = 5.
#
# Path 0 → 2 → 3 → 4
#
# Node 3 is offline, so this path is invalid regardless of cost.
#
# Path 0 → 2 → 4
#
# Total cost = 6 + 6 = 12 <= k, so this path is valid.
#
# The minimum edge‐cost along this path is min(6, 6) = 6.
#
# Among the two valid paths, their scores are 5 and 6. Therefore, the
# answer is 6.
#
# Constraints:
#
# n == online.length
#
# 2 <= n <= 5 * 10^4
#
# 0 <= m == edges.length <= min(10^5, n * (n - 1) / 2)
#
# edges[i] = [u_i, v_i, cost_i]
#
# 0 <= u_i, v_i < n
#
# u_i != v_i
#
# 0 <= cost_i <= 10^9
#
# 0 <= k <= 5 * 10^13
#
# online[i] is either true or false, and both online[0] and online[n − 1]
# are true.
#
# The given graph is a directed acyclic graph.
#

# @lc code=start

from typing import List


class Solution:
    def findMaxPathScore(
        self, edges: List[List[int]], online: List[bool], k: int
    ) -> int:
        """
        Interview explanation:
        On a DAG, maximize the bottleneck (min edge cost) of a 0→n-1 path that
        only uses online nodes and has total cost ≤ k.

        Algorithm:
        - Binary search bottleneck x; keep edges with cost ≥ x into online nodes.
        - Topo DP: min path cost from 0; feasible if dist[n-1] ≤ k.

        Complexity: O((n+E) log C) time, O(n+E) space.
        """
        n = len(online)
        adj: List[List[tuple]] = [[] for _ in range(n)]
        indeg = [0] * n
        max_c = 0
        for u, v, c in edges:
            adj[u].append((v, c))
            indeg[v] += 1
            max_c = max(max_c, c)

        order: List[int] = []
        deg = indeg[:]
        q = [i for i in range(n) if deg[i] == 0]
        while q:
            u = q.pop()
            order.append(u)
            for v, _ in adj[u]:
                deg[v] -= 1
                if deg[v] == 0:
                    q.append(v)

        def feasible(x: int) -> bool:
            INF = 10**30
            dist = [INF] * n
            dist[0] = 0
            for u in order:
                if dist[u] >= INF:
                    continue
                for v, c in adj[u]:
                    if c < x or not online[v]:
                        continue
                    nv = dist[u] + c
                    if nv < dist[v]:
                        dist[v] = nv
            return dist[n - 1] <= k

        lo, hi, ans = 0, max_c, -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if feasible(mid):
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans
# @lc code=end
