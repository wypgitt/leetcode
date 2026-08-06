#
# @lc app=leetcode id=1971 lang=python3
#
# [1971] Find if Path Exists in Graph
#
# https://leetcode.com/problems/find-if-path-exists-in-graph/description/
#
# algorithms
# Easy (55.65%)
# Likes:    4399
# Dislikes: 257
# Total Accepted:    737K
# Total Submissions: 1.3M
# Testcase Example:  "3"
#
# There is a bi-directional graph with n vertices, where each vertex is labeled
# from 0 to n - 1 (inclusive). The edges in the graph are represented as a 2D
# integer array edges, where each edges[i] = [u_i, v_i] denotes a
# bi-directional edge between vertex u_i and vertex v_i. Every vertex pair is
# connected by at most one edge, and no vertex has an edge to itself.
#
# You want to determine if there is a valid path that exists from vertex source
# to vertex destination.
#
# Given edges and the integers n, source, and destination, return true if there
# is a valid path from source to destination, or false otherwise.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[1,2],[2,0]], source = 0, destination = 2
# Output: true
# Explanation: There are two paths from vertex 0 to vertex 2:
# - 0 → 1 → 2
# - 0 → 2
#
# Example 2:
#
# Input: n = 6, edges = [[0,1],[0,2],[3,5],[5,4],[4,3]], source = 0,
# destination = 5
# Output: false
# Explanation: There is no path from vertex 0 to vertex 5.
#
# Constraints:
#
# 1 <= n <= 2 * 10^5
#
# 0 <= edges.length <= 2 * 10^5
#
# edges[i].length == 2
#
# 0 <= u_i, v_i <= n - 1
#
# u_i != v_i
#
# 0 <= source, destination <= n - 1
#
# There are no duplicate edges.
#
# There are no self edges.
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def validPath(self, n: int, edges: List[List[int]], source: int, destination: int) -> bool:
        """
        Interview explanation:
        Undirected graph path existence from source to destination — BFS/DFS/UF.

        Algorithm:
        - Build adjacency; BFS from source; return whether destination visited.

        Complexity: O(n + m) time, O(n + m) space.
        """
        if source == destination:
            return True
        g = defaultdict(list)
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        seen = {source}
        q = deque([source])
        while q:
            u = q.popleft()
            for v in g[u]:
                if v == destination:
                    return True
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        return False

    def validPath_uf(self, n: int, edges: List[List[int]], source: int, destination: int) -> bool:
        """
        Interview explanation:
        Classic alternate: Union-Find; path exists iff same component.

        Algorithm:
        - Union all edges; return find(source)==find(destination).

        Complexity: O(n + m α(n)) time, O(n) space.
        """
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for u, v in edges:
            parent[find(u)] = find(v)
        return find(source) == find(destination)

    def validPath_dfs(self, n: int, edges: List[List[int]], source: int, destination: int) -> bool:
        """
        Interview explanation:
        Alternate iterative DFS / stack traversal of the undirected graph.

        Algorithm:
        - Stack from source; mark seen; success if destination popped/seen.

        Complexity: O(n + m) time, O(n + m) space.
        """
        if source == destination:
            return True
        g = defaultdict(list)
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        seen = {source}
        st = [source]
        while st:
            u = st.pop()
            for v in g[u]:
                if v == destination:
                    return True
                if v not in seen:
                    seen.add(v)
                    st.append(v)
        return False
# @lc code=end

