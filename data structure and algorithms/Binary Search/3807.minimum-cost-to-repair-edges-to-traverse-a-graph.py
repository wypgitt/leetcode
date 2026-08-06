#
# @lc app=leetcode id=3807 lang=python3
#
# [3807] Minimum Cost to Repair Edges to Traverse a Graph
#
# https://leetcode.com/problems/minimum-cost-to-repair-edges-to-traverse-a-graph/description/
#
# algorithms
# Medium (54.93%)
# Likes:    7
# Dislikes: 1
# Total Accepted:    629
# Total Submissions: 1.1K
# Testcase Example:  "3\n[[0,1,10],[1,2,10],[0,2,100]]\n1"
#
#
# You are given an undirected graph with n nodes labeled from 0 to n - 1.
# The graph consists of m edges represented by a 2D integer array edges,
# where edges[i] = [u_i, v_i, w_i] indicates that there is an edge between
# nodes u_i and v_i with a repair cost of w_i.
#
# You are also given an integer k. Initially, all edges are damaged.
#
# You may choose a non-negative integer money and repair all edges whose
# repair cost is less than or equal to money. All other edges remain
# damaged and cannot be used.
#
# You want to travel from node 0 to node n - 1 using at most k edges.
#
# Return an integer denoting the minimum amount of money required to make
# this possible, or return -1 if it is impossible.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1,10],[1,2,10],[0,2,100]], k = 1
#
# Output: 100
#
# Explanation:
#
# The only valid path using at most k = 1 edge is 0 -> 2, which requires
# repairing the edge with cost 100. Therefore, the minimum required amount
# of money is 100.
#
# Example 2:
#
# Input: n = 6, edges =
# [[0,2,5],[2,3,6],[3,4,7],[4,5,5],[0,1,10],[1,5,12],[0,3,9],[1,2,8],[2,4,11]],
# k = 2
#
# Output: 12
#
# Explanation:
#
# With money = 12, all edges with repair cost at most 12 become usable.
#
# This allows the path 0 -> 1 -> 5, which uses exactly 2 edges and reaches
# node 5.
#
# If money < 12, there is no available path of length at most k = 2 from
# node 0 to node 5.
#
# Therefore, the minimum required money is 12.
#
# Example 3:
#
# ​​​​​​​
#
# Input: n = 3, edges = [[0,1,1]], k = 1
#
# Output: -1
#
# Explanation:
#
# It is impossible to reach node 2 from node 0 using any amount of money.
# Therefore, the answer is -1.
#
# Constraints:
#
# 2 <= n <= 5 * 10^4
#
# 1 <= edges.length == m <= 10^5
#
# edges[i] = [u_i, v_i, w_i]
#
# 0 <= u_i, v_i < n
#
# 1 <= w_i <= 10^9
#
# 1 <= k <= n
#
# There are no self-loops or duplicate edges in the graph.
#

# @lc code=start

from typing import List


class Solution:
    def minCost(self, n: int, edges: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Money is the max repair cost we can afford. Larger money only adds
        edges, so binary search the minimum money that admits a path from 0
        to n-1 of length <= k.

        Algorithm:
        - Sort edges by cost; binary search the prefix of cheapest edges.
        - For a candidate prefix, BFS and check dist[n-1] <= k.

        Complexity: O((n+m) log m) time, O(n+m) space.
        """
        edges.sort(key=lambda e: e[2])
        m = len(edges)

        def check(idx: int) -> bool:
            g = [[] for _ in range(n)]
            for u, v, _ in edges[: idx + 1]:
                g[u].append(v)
                g[v].append(u)
            q = [0]
            vis = [False] * n
            vis[0] = True
            dist = 0
            while q:
                nq = []
                for u in q:
                    if u == n - 1:
                        return dist <= k
                    for v in g[u]:
                        if not vis[v]:
                            vis[v] = True
                            nq.append(v)
                q = nq
                dist += 1
            return False

        l, r = 0, m - 1
        while l < r:
            mid = (l + r) >> 1
            if check(mid):
                r = mid
            else:
                l = mid + 1
        return edges[l][2] if check(l) else -1
# @lc code=end
