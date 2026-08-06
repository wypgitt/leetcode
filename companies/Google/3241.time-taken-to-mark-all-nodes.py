#
# @lc app=leetcode id=3241 lang=python3
#
# [3241] Time Taken to Mark All Nodes
#
# https://leetcode.com/problems/time-taken-to-mark-all-nodes/description/
#
# algorithms
# Hard (29.02%)
# Likes:    149
# Dislikes: 7
# Total Accepted:    7.2K
# Total Submissions: 24.9K
# Testcase Example:  "[[0,1],[0,2]]"
#
#
# There exists an undirected tree with n nodes numbered 0 to n - 1. You
# are given a 2D integer array edges of length n - 1, where edges[i] =
# [u_i, v_i] indicates that there is an edge between nodes u_i and v_i in
# the tree.
#
# Initially, all nodes are unmarked. For each node i:
#
# If i is odd, the node will get marked at time x if there is at least one
# node adjacent to it which was marked at time x - 1.
#
# If i is even, the node will get marked at time x if there is at least
# one node adjacent to it which was marked at time x - 2.
#
# Return an array times where times[i] is the time when all nodes get
# marked in the tree, if you mark node i at time t = 0.
#
# Note that the answer for each times[i] is independent, i.e. when you
# mark node i all other nodes are unmarked.
#
# Example 1:
#
# Input: edges = [[0,1],[0,2]]
#
# Output: [2,4,3]
#
# Explanation:
#
# For i = 0:
#
# Node 1 is marked at t = 1, and Node 2 at t = 2.
#
# For i = 1:
#
# Node 0 is marked at t = 2, and Node 2 at t = 4.
#
# For i = 2:
#
# Node 0 is marked at t = 2, and Node 1 at t = 3.
#
# Example 2:
#
# Input: edges = [[0,1]]
#
# Output: [1,2]
#
# Explanation:
#
# For i = 0:
#
# Node 1 is marked at t = 1.
#
# For i = 1:
#
# Node 0 is marked at t = 2.
#
# Example 3:
#
# Input: edges = [[2,4],[0,1],[2,3],[0,2]]
#
# Output: [4,6,3,5,5]
#
# Explanation:
#
# Constraints:
#
# 2 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i].length == 2
#
# 0 <= edges[i][0], edges[i][1] <= n - 1
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start
from typing import List


class Solution:
    def timeTaken(self, edges: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Marking propagates along edges: odd nodes take +1, even nodes +2 from a
        marked neighbor. For each start node, the answer is the longest weighted
        path in the tree. Compute all answers via rerooting DP.

        Algorithm:
        - Edge into v has weight 1 if v odd else 2.
        - Bottom-up: for each node store best / second-best downward times.
        - Top-down: push the best "upward" path into each child; answer is
          max(down, up).

        Complexity: O(n) time, O(n) space.
        """
        n = len(edges) + 1
        g: List[List[int]] = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)

        def cost(x: int) -> int:
            return 1 if x % 2 else 2

        parent = [-1] * n
        order = [0]
        for u in order:
            for v in g[u]:
                if v != parent[u]:
                    parent[v] = u
                    order.append(v)

        best = [0] * n
        second = [0] * n
        best_child = [-1] * n
        for u in reversed(order):
            for v in g[u]:
                if v == parent[u]:
                    continue
                cand = cost(v) + best[v]
                if cand > best[u]:
                    second[u] = best[u]
                    best[u] = cand
                    best_child[u] = v
                elif cand > second[u]:
                    second[u] = cand

        ans = [0] * n
        up = [0] * n
        for u in order:
            ans[u] = max(best[u], up[u])
            for v in g[u]:
                if v == parent[u]:
                    continue
                excl = second[u] if best_child[u] == v else best[u]
                up[v] = cost(u) + max(up[u], excl)
        return ans
# @lc code=end
