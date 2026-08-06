#
# @lc app=leetcode id=743 lang=python3
#
# [743] Network Delay Time
#
# https://leetcode.com/problems/network-delay-time/description/
#
# algorithms
# Medium (61.24%)
# Likes:    8520
# Dislikes: 393
# Total Accepted:    952K
# Total Submissions: 1.6M
# Testcase Example:  "[[2,1,1],[2,3,1],[3,4,1]]"
#
# You are given a network of n nodes, labeled from 1 to n. You are also given
# times, a list of travel times as directed edges times[i] = (u_i, v_i, w_i),
# where u_i is the source node, v_i is the target node, and w_i is the time it
# takes for a signal to travel from source to target.
#
# We will send a signal from a given node k. Return the minimum time it takes
# for all the n nodes to receive the signal. If it is impossible for all the n
# nodes to receive the signal, return -1.
#
# Example 1:
#
# Input: times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2
# Output: 2
#
# Example 2:
#
# Input: times = [[1,2,1]], n = 2, k = 1
# Output: 1
#
# Example 3:
#
# Input: times = [[1,2,1]], n = 2, k = 2
# Output: -1
#
# Constraints:
#
# 1 <= k <= n <= 100
#
# 1 <= times.length <= 6000
#
# times[i].length == 3
#
# 1 <= u_i, v_i <= n
#
# u_i != v_i
#
# 0 <= w_i <= 100
#
# All the pairs (u_i, v_i) are unique. (i.e., no multiple edges.)
#


# @lc code=start
import heapq
from collections import defaultdict
from typing import Dict, List


class Solution:
    def networkDelayTime(self, times: List[List[int]], n: int, k: int) -> int:
        """
        Interview explanation:
        Shortest paths from node k in a weighted digraph; answer is the max
        distance among all nodes (or -1 if some unreachable). Dijkstra with a
        min-heap is the classic approach for non-negative weights.

        Algorithm (Dijkstra):
        - Build adjacency list; dist[k]=0, others inf
        - Pop closest unsettled node; relax outgoing edges
        - Return max(dist) if finite else -1

        Complexity: O((n+e) log n) time, O(n+e) space.
        """
        graph: Dict[int, List[tuple]] = defaultdict(list)
        for u, v, w in times:
            graph[u].append((v, w))
        dist = {i: float("inf") for i in range(1, n + 1)}
        dist[k] = 0
        pq = [(0, k)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in graph[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        ans = max(dist.values())
        return int(ans) if ans < float("inf") else -1

    def networkDelayTime_bellman_ford(
        self, times: List[List[int]], n: int, k: int
    ) -> int:
        """
        Interview explanation:
        Alternate classic: Bellman-Ford relaxes all edges n-1 times; works with
        the same non-negative instance and is simpler to code (slower).

        Algorithm:
        - dist[k]=0; repeat n-1 times: for each edge, relax
        - Return max(dist) or -1

        Complexity: O(n * e) time, O(n) space.
        """
        dist = [float("inf")] * (n + 1)
        dist[k] = 0
        for _ in range(n - 1):
            updated = False
            for u, v, w in times:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    updated = True
            if not updated:
                break
        ans = max(dist[1:])
        return int(ans) if ans < float("inf") else -1
# @lc code=end

