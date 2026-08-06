#
# @lc app=leetcode id=3123 lang=python3
#
# [3123] Find Edges in Shortest Paths
#
# https://leetcode.com/problems/find-edges-in-shortest-paths/description/
#
# algorithms
# Hard (46.53%)
# Likes:    328
# Dislikes: 5
# Total Accepted:    20.7K
# Total Submissions: 44.5K
# Testcase Example:  "6\n[[0,1,4],[0,2,1],[1,3,2],[1,4,3],[1,5,1],[2,3,1],[3,5,3],[4,5,2]]"
#
#
# You are given an undirected weighted graph of n nodes numbered from 0 to
# n - 1. The graph consists of m edges represented by a 2D array edges,
# where edges[i] = [a_i, b_i, w_i] indicates that there is an edge between
# nodes a_i and b_i with weight w_i.
#
# Consider all the shortest paths from node 0 to node n - 1 in the graph.
# You need to find a boolean array answer where answer[i] is true if the
# edge edges[i] is part of at least one shortest path. Otherwise,
# answer[i] is false.
#
# Return the array answer.
#
# Note that the graph may not be connected.
#
# Example 1:
#
# Input: n = 6, edges =
# [[0,1,4],[0,2,1],[1,3,2],[1,4,3],[1,5,1],[2,3,1],[3,5,3],[4,5,2]]
#
# Output: [true,true,true,false,true,true,true,false]
#
# Explanation:
#
# The following are all the shortest paths between nodes 0 and 5:
#
# The path 0 -> 1 -> 5: The sum of weights is 4 + 1 = 5.
#
# The path 0 -> 2 -> 3 -> 5: The sum of weights is 1 + 1 + 3 = 5.
#
# The path 0 -> 2 -> 3 -> 1 -> 5: The sum of weights is 1 + 1 + 2 + 1 = 5.
#
# Example 2:
#
# Input: n = 4, edges = [[2,0,1],[0,1,1],[0,3,4],[3,2,2]]
#
# Output: [true,false,false,true]
#
# Explanation:
#
# There is one shortest path between nodes 0 and 3, which is the path 0 ->
# 2 -> 3 with the sum of weights 1 + 2 = 3.
#
# Constraints:
#
# 2 <= n <= 5 * 10^4
#
# m == edges.length
#
# 1 <= m <= min(5 * 10^4, n * (n - 1) / 2)
#
# 0 <= a_i, b_i < n
#
# a_i != b_i
#
# 1 <= w_i <= 10^5
#
# There are no repeated edges.
#

# @lc code=start
import heapq
from typing import List


class Solution:
    def findAnswer(self, n: int, edges: List[List[int]]) -> List[bool]:
        """
        Interview explanation:
        An edge (u,v,w) lies on some 0..n-1 shortest path iff
        dist(0,u)+w+dist(v,n-1) equals dist(0,n-1) (or u/v swapped).

        Algorithm:
        - Dijkstra from 0 and from n-1 on the undirected weighted graph.
        - Mark edge true when either orientation reconstructs the global shortest.

        Complexity: O((n+m) log n) time, O(n+m) space.
        """
        g: List[List[tuple]] = [[] for _ in range(n)]
        for a, b, w in edges:
            g[a].append((b, w))
            g[b].append((a, w))

        INF = 10**18

        def dijkstra(src: int) -> List[int]:
            dist = [INF] * n
            dist[src] = 0
            pq = [(0, src)]
            while pq:
                d, u = heapq.heappop(pq)
                if d != dist[u]:
                    continue
                for v, w in g[u]:
                    nd = d + w
                    if nd < dist[v]:
                        dist[v] = nd
                        heapq.heappush(pq, (nd, v))
            return dist

        d0 = dijkstra(0)
        dn = dijkstra(n - 1)
        target = d0[n - 1]
        ans = []
        for a, b, w in edges:
            on_path = target < INF and (
                d0[a] + w + dn[b] == target or d0[b] + w + dn[a] == target
            )
            ans.append(on_path)
        return ans
# @lc code=end
