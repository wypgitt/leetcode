#
# @lc app=leetcode id=785 lang=python3
#
# [785] Is Graph Bipartite?
#
# https://leetcode.com/problems/is-graph-bipartite/description/
#
# algorithms
# Medium (59.7%)
# Likes:    9379
# Dislikes: 421
# Total Accepted:    928K
# Total Submissions: 1.6M
# Testcase Example:  "[[1,2,3],[0,2],[0,1,3],[0,2]]"
#
# There is an undirected graph with n nodes, where each node is numbered
# between 0 and n - 1. You are given a 2D array graph, where graph[u] is an
# array of nodes that node u is adjacent to. More formally, for each v in
# graph[u], there is an undirected edge between node u and node v. The graph
# has the following properties:
#
# There are no self-edges (graph[u] does not contain u).
#
# There are no parallel edges (graph[u] does not contain duplicate values).
#
# If v is in graph[u], then u is in graph[v] (the graph is undirected).
#
# The graph may not be connected, meaning there may be two nodes u and v such
# that there is no path between them.
#
# A graph is bipartite if the nodes can be partitioned into two independent
# sets A and B such that every edge in the graph connects a node in set A and a
# node in set B.
#
# Return true if and only if it is bipartite.
#
# Example 1:
#
# Input: graph = [[1,2,3],[0,2],[0,1,3],[0,2]]
# Output: false
# Explanation: There is no way to partition the nodes into two independent sets
# such that every edge connects a node in one and a node in the other.
#
# Example 2:
#
# Input: graph = [[1,3],[0,2],[1,3],[0,2]]
# Output: true
# Explanation: We can partition the nodes into two sets: {0, 2} and {1, 3}.
#
# Constraints:
#
# graph.length == n
#
# 1 <= n <= 100
#
# 0 <= graph[u].length < n
#
# 0 <= graph[u][i] <= n - 1
#
# graph[u] does not contain u.
#
# All the values of graph[u] are unique.
#
# If graph[u] contains v, then graph[v] contains u.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def isBipartite(self, graph: List[List[int]]) -> bool:
        """
        Interview explanation:
        Color nodes with 2 colors so every edge joins different colors (BFS).
        Process each component; conflict on a neighbor ⇒ not bipartite.

        Algorithm (BFS coloring):
        - color[u] = 0/1/-1 uncolored.
        - For each uncolored u: BFS; assign opposite color to neighbors.

        Complexity: O(V+E) time, O(V) space.
        """
        n = len(graph)
        color = [-1] * n
        for start in range(n):
            if color[start] != -1:
                continue
            color[start] = 0
            q = deque([start])
            while q:
                u = q.popleft()
                for v in graph[u]:
                    if color[v] == -1:
                        color[v] = color[u] ^ 1
                        q.append(v)
                    elif color[v] == color[u]:
                        return False
        return True

    def isBipartite_dfs(self, graph: List[List[int]]) -> bool:
        """
        Interview explanation:
        Alternate classic: DFS coloring — same 2-color invariant, recurse on
        neighbors with flipped color; conflict ⇒ False.

        Algorithm:
        - DFS(u,c): color[u]=c; for each neighbor, DFS with c^1 or check conflict.

        Complexity: O(V+E) time, O(V) space.
        """
        n = len(graph)
        color = [-1] * n

        def dfs(u: int, c: int) -> bool:
            color[u] = c
            for v in graph[u]:
                if color[v] == -1:
                    if not dfs(v, c ^ 1):
                        return False
                elif color[v] == color[u]:
                    return False
            return True

        for i in range(n):
            if color[i] == -1 and not dfs(i, 0):
                return False
        return True
# @lc code=end

