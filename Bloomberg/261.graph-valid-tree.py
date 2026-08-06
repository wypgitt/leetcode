#
# @lc app=leetcode id=261 lang=python3
#
# [261] Graph Valid Tree
#
# https://leetcode.com/problems/graph-valid-tree/description/
#
# algorithms
# Medium (50.09%)
# Likes:    3476
# Dislikes: 116
# Total Accepted:    544.7K
# Total Submissions: 1.1M
# Testcase Example:  "5\n[[0,1],[0,2],[0,3],[1,4]]"
#
#
# You have a graph of n nodes labeled from 0 to n - 1. You are given an
# integer n and a list of edges where edges[i] = [a_i, b_i] indicates that
# there is an undirected edge between nodes a_i and b_i in the graph.
#
# Return true if the edges of the given graph make up a valid tree, and
# false otherwise.
#
# Example 1:
#
# Input: n = 5, edges = [[0,1],[0,2],[0,3],[1,4]]
# Output: true
#
# Example 2:
#
# Input: n = 5, edges = [[0,1],[1,2],[2,3],[1,3],[1,4]]
# Output: false
#
# Constraints:
#
# 1 <= n <= 2000
#
# 0 <= edges.length <= 5000
#
# edges[i].length == 2
#
# 0 <= a_i, b_i < n
#
# a_i != b_i
#
# There are no self-loops or repeated edges.
#
# @lc code=start
from collections import defaultdict, deque
from typing import Dict, List, Set


class Solution:
    def validTree(self, n: int, edges: List[List[int]]) -> bool:
        """
        Interview explanation:
        An undirected graph is a tree iff it is connected and has n-1 edges
        (equivalently: no cycles and connected). Union-Find: each edge should
        unite two different components; finally one component.

        Algorithm:
        - Early reject if len(edges) != n - 1.
        - Union edges; if find(u) == find(v), cycle -> False.
        - Return True (edge count already ensures connectivity if no cycle).

        Complexity: O(n + m) α practically, O(n) space.
        """
        if len(edges) != n - 1:
            return False

        parent = list(range(n))
        rank = [0] * n

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> bool:
            ra, rb = find(a), find(b)
            if ra == rb:
                return False
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1
            return True

        for u, v in edges:
            if not union(u, v):
                return False
        return True

    def validTreeDFS(self, n: int, edges: List[List[int]]) -> bool:
        """
        Interview explanation:
        DFS/BFS alternate: build adjacency list; require exactly n-1 edges, then
        traverse from 0 and verify all n nodes are visited (connected + acyclic
        via edge count).

        Algorithm:
        - If len(edges) != n-1: False.
        - BFS/DFS from 0; return len(visited) == n.

        Complexity: O(n + m) time, O(n + m) space.
        """
        if len(edges) != n - 1:
            return False
        graph: Dict[int, List[int]] = defaultdict(list)
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)

        seen: Set[int] = set()
        q = deque([0])
        seen.add(0)
        while q:
            node = q.popleft()
            for nei in graph[node]:
                if nei not in seen:
                    seen.add(nei)
                    q.append(nei)
        return len(seen) == n
# @lc code=end
