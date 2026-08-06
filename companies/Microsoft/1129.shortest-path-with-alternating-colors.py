#
# @lc app=leetcode id=1129 lang=python3
#
# [1129] Shortest Path with Alternating Colors
#
# https://leetcode.com/problems/shortest-path-with-alternating-colors/description/
#
# algorithms
# Medium (48.18%)
# Likes:    3737
# Dislikes: 207
# Total Accepted:    160K
# Total Submissions: 332K
# Testcase Example:  "3"
#
# You are given an integer n, the number of nodes in a directed graph where the
# nodes are labeled from 0 to n - 1. Each edge is red or blue in this graph,
# and there could be self-edges and parallel edges.
#
# You are given two arrays redEdges and blueEdges where:
#
# redEdges[i] = [a_i, b_i] indicates that there is a directed red edge from
# node a_i to node b_i in the graph, and
#
# blueEdges[j] = [u_j, v_j] indicates that there is a directed blue edge from
# node u_j to node v_j in the graph.
#
# Return an array answer of length n, where each answer[x] is the length of the
# shortest path from node 0 to node x such that the edge colors alternate along
# the path, or -1 if such a path does not exist.
#
# Example 1:
#
# Input: n = 3, redEdges = [[0,1],[1,2]], blueEdges = []
# Output: [0,1,-1]
#
# Example 2:
#
# Input: n = 3, redEdges = [[0,1]], blueEdges = [[2,1]]
# Output: [0,1,-1]
#
# Constraints:
#
# 1 <= n <= 100
#
# 0 <= redEdges.length, blueEdges.length <= 400
#
# redEdges[i].length == blueEdges[j].length == 2
#
# 0 <= a_i, b_i, u_j, v_j < n
#

# @lc code=start
from typing import List, Deque, Tuple
from collections import deque


class Solution:
    def shortestAlternatingPaths(
        self, n: int, redEdges: List[List[int]], blueEdges: List[List[int]]
    ) -> List[int]:
        """
        Interview explanation:
        Shortest path from 0 with alternating red/blue edges. State is
        (node, last_color); BFS over both colors starting from 0.

        Algorithm (BFS):
        - Build adj[0]=red, adj[1]=blue.
        - Queue (node, color, dist); mark visited[node][color].
        - Extend via opposite color edges.

        Complexity: O(n + E) time/space.
        """
        adj: List[List[List[int]]] = [[[] for _ in range(n)] for _ in range(2)]
        for u, v in redEdges:
            adj[0][u].append(v)
        for u, v in blueEdges:
            adj[1][u].append(v)

        ans = [-1] * n
        ans[0] = 0
        visited = [[False] * 2 for _ in range(n)]
        q: Deque[Tuple[int, int, int]] = deque([(0, 0, 0), (0, 1, 0)])
        visited[0][0] = visited[0][1] = True

        while q:
            node, color, dist = q.popleft()
            nxt = 1 - color
            for nei in adj[nxt][node]:
                if not visited[nei][nxt]:
                    visited[nei][nxt] = True
                    if ans[nei] == -1:
                        ans[nei] = dist + 1
                    q.append((nei, nxt, dist + 1))
        return ans
# @lc code=end
