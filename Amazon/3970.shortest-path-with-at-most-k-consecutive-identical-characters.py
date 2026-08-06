#
# @lc app=leetcode id=3970 lang=python3
#
# [3970] Shortest Path With At Most K Consecutive Identical Characters
#
# https://leetcode.com/problems/shortest-path-with-at-most-k-consecutive-identical-characters/description/
#
# algorithms
# Medium (45.12%)
# Likes:    89
# Dislikes: 5
# Total Accepted:    18.2K
# Total Submissions: 40.4K
# Testcase Example:  "3\n[[0,1,1],[1,2,1],[0,2,3]]\n\"aab\"\n1"
#
#
# You are given an integer n representing the number of nodes in a
# directed weighted graph, numbered from 0 to n - 1. This is represented
# by a 2D integer array edges, where edges[i] = [u_i, v_i, w_i] represents
# a directed edge from node u_i to node v_i with weight w_i.
#
# You are also given a string labels of length n, where labels[i] is the
# character assigned to node i, and an integer k.
#
# Return the minimum total edge weight of a path from node 0 to node n - 1
# such that the concatenation of the labels of the nodes along the path
# contains at most k consecutive identical characters. If no valid path
# exists, return -1.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1,1],[1,2,1],[0,2,3]], labels = "aab", k = 1
#
# Output: 3
#
# Explanation:
#
# The optimal valid path from node 0 to node 2 is as follows:
#
# Use edges[2] = [0, 2, 3] to reach node 2 with a weight w_i = 3.
#
# The corresponding concatenation of labels is "ab", which satisfies at
# most k = 1 consecutive identical characters. Thus, the answer is 3.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1,1],[1,2,1],[0,2,3]], labels = "aab", k = 2
#
# Output: 2
#
# Explanation:
#
# The optimal valid path from node 0 to node 2 is as follows:
#
# Use edges[0] = [0, 1, 1] to reach node 1 with weight w_i = 1.
#
# Use edges[1] = [1, 2, 1] to reach node 2 with weight w_i = 1.
#
# The corresponding concatenation of labels is "aab", which satisfies at
# most k = 2 consecutive identical characters. Thus, the answer is 2.
#
# Example 3:
#
# Input: n = 3, edges = [[0,1,1],[1,2,1]], labels = "aaa", k = 2
#
# Output: -1
#
# Explanation:
#
# There is no valid path from node 0 to node 2 that satisfies at most k =
# 2 consecutive identical characters. Thus, the answer is -1.
#
# Constraints:
#
# 1 <= n == labels.length <= 5 * 10^4
#
# 0 <= edges.length <= 5 * 10^4
#
# edges[i] == [u_i, v_i, w_i]
#
# 0 <= u_i, v_i <= n - 1
#
# u_i != v_i
#
# 1 <= w_i <= 10^4
#
# labels consists of lowercase English letters
#
# 1 <= k <= 50
#

# @lc code=start

import heapq
from math import inf
from typing import List


class Solution:
    def shortestPath(self, n: int, edges: List[List[int]], labels: str, k: int) -> int:
        """
        Interview explanation:
        Edge weights need Dijkstra, and validity depends on the current run length
        of identical labels, so expand the state to (node, consecutive_count).

        Algorithm:
        - Build the directed graph.
        - Dijkstra on (node, cnt); start at (0, 1).
        - Transition u->v: cnt' = cnt+1 if labels match else 1; skip if cnt' > k.
        - Return the first time n-1 is popped (minimum distance).

        Complexity: O((n*k + m*k) log(n*k)) time, O(n*k) space.
        """
        g = [[] for _ in range(n)]
        for u, v, w in edges:
            g[u].append((v, w))
        dist = [[inf] * (k + 1) for _ in range(n)]
        dist[0][1] = 0
        pq = [(0, 0, 1)]
        while pq:
            d, u, cnt = heapq.heappop(pq)
            if d > dist[u][cnt]:
                continue
            if u == n - 1:
                return d
            for v, w in g[u]:
                nc = cnt + 1 if labels[u] == labels[v] else 1
                if nc > k:
                    continue
                nd = d + w
                if nd < dist[v][nc]:
                    dist[v][nc] = nd
                    heapq.heappush(pq, (nd, v, nc))
        return -1
# @lc code=end
