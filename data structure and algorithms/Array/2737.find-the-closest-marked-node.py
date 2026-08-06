#
# @lc app=leetcode id=2737 lang=python3
#
# [2737] Find the Closest Marked Node
#
# https://leetcode.com/problems/find-the-closest-marked-node/description/
#
# algorithms
# Medium (65.55%)
# Likes:    60
# Dislikes: 6
# Total Accepted:    7.5K
# Total Submissions: 11.5K
# Testcase Example:  "4\n[[0,1,1],[1,2,3],[2,3,2],[0,3,4]]\n0\n[2,3]"
#
#
# You are given a positive integer n which is the number of nodes of a
# 0-indexed directed weighted graph and a 0-indexed 2D array edges where
# edges[i] = [u_i, v_i, w_i] indicates that there is an edge from node u_i
# to node v_i with weight w_i.
#
# You are also given a node s and a node array marked; your task is to
# find the minimum distance from s to any of the nodes in marked.
#
# Return an integer denoting the minimum distance from s to any node in
# marked or -1 if there are no paths from s to any of the marked nodes.
#
# Example 1:
#
# Input: n = 4, edges = [[0,1,1],[1,2,3],[2,3,2],[0,3,4]], s = 0, marked =
# [2,3]
# Output: 4
# Explanation: There is one path from node 0 (the green node) to node 2 (a
# red node), which is 0->1->2, and has a distance of 1 + 3 = 4.
# There are two paths from node 0 to node 3 (a red node), which are
# 0->1->2->3 and 0->3, the first one has a distance of 1 + 3 + 2 = 6 and
# the second one has a distance of 4.
# The minimum of them is 4.
#
# Example 2:
#
# Input: n = 5, edges = [[0,1,2],[0,2,4],[1,3,1],[2,3,3],[3,4,2]], s = 1,
# marked = [0,4]
# Output: 3
# Explanation: There are no paths from node 1 (the green node) to node 0
# (a red node).
# There is one path from node 1 to node 4 (a red node), which is 1->3->4,
# and has a distance of 1 + 2 = 3.
# So the answer is 3.
#
# Example 3:
#
# Input: n = 4, edges = [[0,1,1],[1,2,3],[2,3,2]], s = 3, marked = [0,1]
# Output: -1
# Explanation: There are no paths from node 3 (the green node) to any of
# the marked nodes (the red nodes), so the answer is -1.
#
# Constraints:
#
# 2 <= n <= 500
#
# 1 <= edges.length <= 10^4
#
# edges[i].length = 3
#
# 0 <= edges[i][0], edges[i][1] <= n - 1
#
# 1 <= edges[i][2] <= 10^6
#
# 1 <= marked.length <= n - 1
#
# 0 <= s, marked[i] <= n - 1
#
# s != marked[i]
#
# marked[i] != marked[j] for every i != j
#
# The graph might have repeated edges.
#
# The graph is generated such that it has no self-loops.
#
# @lc code=start
import heapq
from typing import List


class Solution:
    def minimumDistance(self, n: int, edges: List[List[int]], s: int, marked: List[int]) -> int:
        """
        Interview explanation:
        Premium. Directed weighted graph; min distance from s to any node in marked, else -1.

        Algorithm:
        - Dijkstra from s; stop early when popping a marked node; else min dist among marked.

        Complexity: O((n+m) log n) time, O(n+m) space.
        """
        g = [[] for _ in range(n)]
        for u, v, w in edges:
            g[u].append((v, w))
        mark = set(marked)
        dist = [10**18] * n
        dist[s] = 0
        pq = [(0, s)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            if u in mark:
                return d
            for v, w in g[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        return -1

    def minimumDistance_dijkstra(self, n: int, edges: List[List[int]], s: int, marked: List[int]) -> int:
        """
        Interview explanation:
        Alternate Dijkstra naming.

        Algorithm:
        - Same early-exit Dijkstra.

        Complexity: O((n+m) log n) time, O(n+m) space.
        """
        return self.minimumDistance(n, edges, s, marked)
# @lc code=end
