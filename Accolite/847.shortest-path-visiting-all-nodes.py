#
# @lc app=leetcode id=847 lang=python3
#
# [847] Shortest Path Visiting All Nodes
#
# https://leetcode.com/problems/shortest-path-visiting-all-nodes/description/
#
# algorithms
# Hard (66.22%)
# Likes:    4679
# Dislikes: 183
# Total Accepted:    158K
# Total Submissions: 238K
# Testcase Example:  "[[1,2,3],[0],[0],[0]]"
#
# You have an undirected, connected graph of n nodes labeled from 0 to n - 1.
# You are given an array graph where graph[i] is a list of all the nodes
# connected with node i by an edge.
#
# Return the length of the shortest path that visits every node. You may start
# and stop at any node, you may revisit nodes multiple times, and you may reuse
# edges.
#
# Example 1:
#
# Input: graph = [[1,2,3],[0],[0],[0]]
# Output: 4
# Explanation: One possible path is [1,0,2,0,3]
#
# Example 2:
#
# Input: graph = [[1],[0,2,4],[1,3,4],[2],[1,2]]
# Output: 4
# Explanation: One possible path is [0,1,4,2,3]
#
# Constraints:
#
# n == graph.length
#
# 1 <= n <= 12
#
# 0 <= graph[i].length < n
#
# graph[i] does not contain i.
#
# If graph[a] contains b, then graph[b] contains a.
#
# The input graph is always connected.
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def shortestPathLength(self, graph: List[List[int]]) -> int:
        """
        Interview explanation:
        Shortest path visiting every node (nodes revisitable). State = (node,
        bitmask of visited). Multi-source BFS from all starts with their bit set.

        Algorithm (BFS + bitmask):
        - n≤12; state space n*2^n; queue (u, mask, dist); done when mask==full.

        Complexity: O(n^2 * 2^n) time, O(n * 2^n) space.
        """
        n = len(graph)
        full = (1 << n) - 1
        q = deque()
        seen = [[False] * (1 << n) for _ in range(n)]
        for i in range(n):
            q.append((i, 1 << i, 0))
            seen[i][1 << i] = True
        while q:
            u, mask, d = q.popleft()
            if mask == full:
                return d
            for v in graph[u]:
                nmask = mask | (1 << v)
                if not seen[v][nmask]:
                    seen[v][nmask] = True
                    q.append((v, nmask, d + 1))
        return 0
# @lc code=end
