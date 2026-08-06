#
# @lc app=leetcode id=1514 lang=python3
#
# [1514] Path with Maximum Probability
#
# https://leetcode.com/problems/path-with-maximum-probability/description/
#
# algorithms
# Medium (65.69%)
# Likes:    3931
# Dislikes: 110
# Total Accepted:    386K
# Total Submissions: 587K
# Testcase Example:  "3"
#
# You are given an undirected weighted graph of n nodes (0-indexed),
# represented by an edge list where edges[i] = [a, b] is an undirected edge
# connecting the nodes a and b with a probability of success of traversing that
# edge succProb[i].
#
# Given two nodes start and end, find the path with the maximum probability of
# success to go from start to end and return its success probability.
#
# If there is no path from start to end, return 0. Your answer will be accepted
# if it differs from the correct answer by at most 1e-5.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[1,2],[0,2]], succProb = [0.5,0.5,0.2], start =
# 0, end = 2
# Output: 0.25000
# Explanation: There are two paths from start to end, one having a probability
# of success = 0.2 and the other has 0.5 * 0.5 = 0.25.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1],[1,2],[0,2]], succProb = [0.5,0.5,0.3], start =
# 0, end = 2
# Output: 0.30000
#
# Example 3:
#
# Input: n = 3, edges = [[0,1]], succProb = [0.5], start = 0, end = 2
# Output: 0.00000
# Explanation: There is no path between 0 and 2.
#
# Constraints:
#
# 2 <= n <= 10^4
#
# 0 <= start, end < n
#
# start != end
#
# 0 <= a, b < n
#
# a != b
#
# 0 <= succProb.length == edges.length <= 2*10^4
#
# 0 <= succProb[i] <= 1
#
# There is at most one edge between every two nodes.
#

# @lc code=start
from typing import List
from collections import defaultdict
import heapq


class Solution:
    def maxProbability(
        self,
        n: int,
        edges: List[List[int]],
        succProb: List[float],
        start_node: int,
        end_node: int,
    ) -> float:
        """
        Interview explanation:
        Max success probability path = max product of edge probs. Dijkstra-like
        with max-heap on probability (multiply instead of add).

        Algorithm:
        - Build weighted adj; best[start]=1; pop max prob; relax neighbors with *.

        Complexity: O((n+m) log n) time, O(n+m) space.
        """
        g = defaultdict(list)
        for (a, b), p in zip(edges, succProb):
            g[a].append((b, p))
            g[b].append((a, p))
        best = [0.0] * n
        best[start_node] = 1.0
        pq = [(-1.0, start_node)]
        while pq:
            neg, u = heapq.heappop(pq)
            prob = -neg
            if u == end_node:
                return prob
            if prob < best[u]:
                continue
            for v, p in g[u]:
                np = prob * p
                if np > best[v]:
                    best[v] = np
                    heapq.heappush(pq, (-np, v))
        return 0.0

    def maxProbability_bf(
        self,
        n: int,
        edges: List[List[int]],
        succProb: List[float],
        start_node: int,
        end_node: int,
    ) -> float:
        """
        Interview explanation:
        Alternate Bellman-Ford style: relax all edges up to n-1 rounds maximizing
        probability (useful when discussing SP variants).

        Algorithm:
        - best[start]=1; repeat n-1: for each edge update both directions if better *.

        Complexity: O(n*m) time, O(n) space.
        """
        best = [0.0] * n
        best[start_node] = 1.0
        for _ in range(n - 1):
            updated = False
            for (a, b), p in zip(edges, succProb):
                if best[a] * p > best[b]:
                    best[b] = best[a] * p
                    updated = True
                if best[b] * p > best[a]:
                    best[a] = best[b] * p
                    updated = True
            if not updated:
                break
        return best[end_node]
# @lc code=end
