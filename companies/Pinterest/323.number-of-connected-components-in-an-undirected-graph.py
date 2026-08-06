#
# @lc app=leetcode id=323 lang=python3
#
# [323] Number of Connected Components in an Undirected Graph
#
# https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/description/
#
# algorithms
# Medium (65.09%)
# Likes:    2821
# Dislikes: 111
# Total Accepted:    550.5K
# Total Submissions: 845.8K
# Testcase Example:  "5\n[[0,1],[1,2],[3,4]]"
#
#
# You have a graph of n nodes. You are given an integer n and an array
# edges where edges[i] = [a_i, b_i] indicates that there is an edge
# between a_i and b_i in the graph.
#
# Return the number of connected components in the graph.
#
# Example 1:
#
# Input: n = 5, edges = [[0,1],[1,2],[3,4]]
# Output: 2
#
# Example 2:
#
# Input: n = 5, edges = [[0,1],[1,2],[2,3],[3,4]]
# Output: 1
#
# Constraints:
#
# 1 <= n <= 2000
#
# 1 <= edges.length <= 5000
#
# edges[i] = [a_i, b_i]
#
# a_i != b_i
#
# There are no repeated edges.
#
# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def countComponents(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Union-Find: each edge merges two components; answer is the number of
        remaining roots after processing all edges.

        Algorithm:
        - parent[i] = i; path-compressed find; union by rank/size.
        - Start with n components; decrement on successful union.
        - Return remaining component count.

        Complexity: O(n + m * α(n)) time, O(n) space.
        """
        parent = list(range(n))
        rank = [0] * n

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        components = n
        for a, b in edges:
            ra, rb = find(a), find(b)
            if ra == rb:
                continue
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1
            components -= 1
        return components

    def countComponents_dfs(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: build adjacency list and DFS/BFS mark each connected
        component; count how many times we start a new traversal.

        Algorithm:
        - For each unvisited node, DFS its component and increment answer.

        Complexity: O(n + m) time and space.
        """
        graph = defaultdict(list)
        for a, b in edges:
            graph[a].append(b)
            graph[b].append(a)

        visited = [False] * n

        def dfs(u: int) -> None:
            visited[u] = True
            for v in graph[u]:
                if not visited[v]:
                    dfs(v)

        count = 0
        for i in range(n):
            if not visited[i]:
                count += 1
                dfs(i)
        return count
# @lc code=end
