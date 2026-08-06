#
# @lc app=leetcode id=2204 lang=python3
#
# [2204] Distance to a Cycle in Undirected Graph
#
# https://leetcode.com/problems/distance-to-a-cycle-in-undirected-graph/description/
#
# algorithms
# Hard (73.91%)
# Likes:    158
# Dislikes: 11
# Total Accepted:    7.6K
# Total Submissions: 10.3K
# Testcase Example:  "7\n[[1,2],[2,4],[4,3],[3,1],[0,1],[5,2],[6,5]]"
#
#
# You are given a positive integer n representing the number of nodes in a
# connected undirected graph containing exactly one cycle. The nodes are
# numbered from 0 to n - 1 (inclusive).
#
# You are also given a 2D integer array edges, where edges[i] = [node1_i,
# node2_i] denotes that there is a bidirectional edge connecting node1_i
# and node2_i in the graph.
#
# The distance between two nodes a and b is defined to be the minimum
# number of edges that are needed to go from a to b.
#
# Return an integer array answer of size n, where answer[i] is the minimum
# distance between the i^th node and any node in the cycle.
#
# Example 1:
#
# Input: n = 7, edges = [[1,2],[2,4],[4,3],[3,1],[0,1],[5,2],[6,5]]
# Output: [1,0,0,0,0,1,2]
# Explanation:
# The nodes 1, 2, 3, and 4 form the cycle.
# The distance from 0 to 1 is 1.
# The distance from 1 to 1 is 0.
# The distance from 2 to 2 is 0.
# The distance from 3 to 3 is 0.
# The distance from 4 to 4 is 0.
# The distance from 5 to 2 is 1.
# The distance from 6 to 2 is 2.
#
# Example 2:
#
# Input: n = 9, edges =
# [[0,1],[1,2],[0,2],[2,6],[6,7],[6,8],[0,3],[3,4],[3,5]]
# Output: [0,0,0,1,2,2,1,2,2]
# Explanation:
# The nodes 0, 1, and 2 form the cycle.
# The distance from 0 to 0 is 0.
# The distance from 1 to 1 is 0.
# The distance from 2 to 2 is 0.
# The distance from 3 to 1 is 1.
# The distance from 4 to 1 is 2.
# The distance from 5 to 1 is 2.
# The distance from 6 to 2 is 1.
# The distance from 7 to 2 is 2.
# The distance from 8 to 2 is 2.
#
# Constraints:
#
# 3 <= n <= 10^5
#
# edges.length == n
#
# edges[i].length == 2
#
# 0 <= node1_i, node2_i <= n - 1
#
# node1_i != node2_i
#
# The graph is connected.
#
# The graph has exactly one cycle.
#
# There is at most one edge between any pair of vertices.
#
# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def distanceToCycle(self, n: int, edges: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Premium. Connected undirected graph with exactly one cycle. For each node
        return distance to the nearest cycle node.

        Algorithm:
        (topo peel + multi-source BFS)
        - Peel degree-1 leaves until cycle remains; BFS from all cycle nodes.

        Complexity: O(n) time, O(n) space.
        """
        g = defaultdict(list)
        deg = [0] * n
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
            deg[u] += 1
            deg[v] += 1
        q = deque(i for i in range(n) if deg[i] == 1)
        on_cycle = [True] * n
        while q:
            u = q.popleft()
            on_cycle[u] = False
            for v in g[u]:
                deg[v] -= 1
                if deg[v] == 1:
                    q.append(v)
        dist = [0] * n
        q = deque()
        seen = [False] * n
        for i in range(n):
            if on_cycle[i]:
                q.append(i)
                seen[i] = True
        while q:
            u = q.popleft()
            for v in g[u]:
                if not seen[v]:
                    seen[v] = True
                    dist[v] = dist[u] + 1
                    q.append(v)
        return dist

    def distanceToCycle_dfs(self, n: int, edges: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Alternate: DFS find cycle via colors/parent, then BFS distances.

        Algorithm:
        - DFS detect back-edge; reconstruct cycle; multi-source BFS.

        Complexity: O(n) time, O(n) space.
        """
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        parent = [-1] * n
        state = [0] * n
        cycle_start = cycle_end = -1

        def dfs(u: int) -> bool:
            nonlocal cycle_start, cycle_end
            state[u] = 1
            for v in g[u]:
                if v == parent[u]:
                    continue
                if state[v] == 0:
                    parent[v] = u
                    if dfs(v):
                        return True
                elif state[v] == 1:
                    cycle_start, cycle_end = v, u
                    return True
            state[u] = 2
            return False

        dfs(0)
        on_cycle = [False] * n
        on_cycle[cycle_start] = True
        cur = cycle_end
        while cur != cycle_start:
            on_cycle[cur] = True
            cur = parent[cur]
        dist = [0] * n
        q = deque(i for i in range(n) if on_cycle[i])
        seen = on_cycle[:]
        while q:
            u = q.popleft()
            for v in g[u]:
                if not seen[v]:
                    seen[v] = True
                    dist[v] = dist[u] + 1
                    q.append(v)
        return dist
# @lc code=end
