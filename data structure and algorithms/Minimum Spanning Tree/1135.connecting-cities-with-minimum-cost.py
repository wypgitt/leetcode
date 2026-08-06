#
# @lc app=leetcode id=1135 lang=python3
#
# [1135] Connecting Cities With Minimum Cost
#
# https://leetcode.com/problems/connecting-cities-with-minimum-cost/description/
#
# algorithms
# Medium (63.62%)
# Likes:    1180
# Dislikes: 60
# Total Accepted:    93.2K
# Total Submissions: 146.5K
# Testcase Example:  "3\n[[1,2,5],[1,3,6],[2,3,1]]"
#
#
# There are n cities labeled from 1 to n. You are given the integer n and
# an array connections where connections[i] = [x_i, y_i, cost_i] indicates
# that the cost of connecting city x_i and city y_i (bidirectional
# connection) is cost_i.
#
# Return the minimum cost to connect all the n cities such that there is
# at least one path between each pair of cities. If it is impossible to
# connect all the n cities, return -1,
#
# The cost is the sum of the connections' costs used.
#
# Example 1:
#
# Input: n = 3, connections = [[1,2,5],[1,3,6],[2,3,1]]
# Output: 6
# Explanation: Choosing any 2 edges will connect all cities so we choose
# the minimum 2.
#
# Example 2:
#
# Input: n = 4, connections = [[1,2,3],[3,4,4]]
# Output: -1
# Explanation: There is no way to connect all cities even if all edges are
# used.
#
# Constraints:
#
# 1 <= n <= 10^4
#
# 1 <= connections.length <= 10^4
#
# connections[i].length == 3
#
# 1 <= x_i, y_i <= n
#
# x_i != y_i
#
# 0 <= cost_i <= 10^5
#
# @lc code=start
from typing import List
import heapq


class Solution:
    def minimumCost(self, n: int, connections: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium MST: connect n cities with min total cost (or -1 if impossible).
        Kruskal with Union-Find is the classic approach.

        Algorithm (Kruskal):
        - Sort edges by cost; union endpoints if different components; add cost.
        - Need n-1 edges; else -1.

        Complexity: O(E log E) time, O(n) space.
        """
        parent = list(range(n + 1))
        rank = [0] * (n + 1)

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

        connections.sort(key=lambda e: e[2])
        cost = 0
        used = 0
        for u, v, w in connections:
            if union(u, v):
                cost += w
                used += 1
                if used == n - 1:
                    return cost
        return -1

    def minimumCost_prim(self, n: int, connections: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic alternate MST: Prim growing a tree from city 1 with a min-heap
        of outgoing edges.

        Algorithm (Prim):
        - Build adjacency; start at 1; repeatedly take cheapest edge to new city.
        - If fewer than n cities visited, return -1.

        Complexity: O(E log E) time, O(n + E) space.
        """
        adj: List[List[tuple]] = [[] for _ in range(n + 1)]
        for u, v, w in connections:
            adj[u].append((w, v))
            adj[v].append((w, u))

        visited = [False] * (n + 1)
        heap = [(0, 1)]
        total = 0
        taken = 0
        while heap and taken < n:
            w, u = heapq.heappop(heap)
            if visited[u]:
                continue
            visited[u] = True
            total += w
            taken += 1
            for nw, v in adj[u]:
                if not visited[v]:
                    heapq.heappush(heap, (nw, v))
        return total if taken == n else -1
# @lc code=end
