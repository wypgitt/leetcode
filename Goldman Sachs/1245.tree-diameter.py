#
# @lc app=leetcode id=1245 lang=python3
#
# [1245] Tree Diameter
#
# https://leetcode.com/problems/tree-diameter/description/
#
# algorithms
# Medium (61.25%)
# Likes:    904
# Dislikes: 26
# Total Accepted:    57.4K
# Total Submissions: 93.7K
# Testcase Example:  "[[0,1],[0,2]]"
#
#
# The diameter of a tree is the number of edges in the longest path in
# that tree.
#
# There is an undirected tree of n nodes labeled from 0 to n - 1. You are
# given a 2D array edges where edges.length == n - 1 and edges[i] = [a_i,
# b_i] indicates that there is an undirected edge between nodes a_i and
# b_i in the tree.
#
# Return the diameter of the tree.
#
# Example 1:
#
# Input: edges = [[0,1],[0,2]]
# Output: 2
# Explanation: The longest path of the tree is the path 1 - 0 - 2.
#
# Example 2:
#
# Input: edges = [[0,1],[1,2],[2,3],[1,4],[4,5]]
# Output: 4
# Explanation: The longest path of the tree is the path 3 - 2 - 1 - 4 - 5.
#
# Constraints:
#
# n == edges.length + 1
#
# 1 <= n <= 10^4
#
# 0 <= a_i, b_i < n
#
# a_i != b_i
#
# @lc code=start
from typing import List
from collections import defaultdict, deque

class Solution:
    def treeDiameter(self, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium. Tree diameter = longest path (#edges). Two BFS: from any node
        find farthest u; from u find farthest v; distance u→v is diameter.

        Algorithm:
        - Build adj; BFS(0)→u; BFS(u)→(v, dist); return dist

        Complexity: O(n) time/space.
        """
        if not edges:
            return 0
        adj = defaultdict(list)
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)

        def bfs(start: int):
            q = deque([(start, 0)])
            seen = {start}
            far_node, far_dist = start, 0
            while q:
                u, d = q.popleft()
                if d > far_dist:
                    far_dist, far_node = d, u
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        q.append((v, d + 1))
            return far_node, far_dist

        u, _ = bfs(0)
        _, diameter = bfs(u)
        return diameter

    def treeDiameter_dfs(self, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: DFS/tree DP — for each node, track top-2 child heights;
        diameter = max over nodes of h1+h2.

        Algorithm:
        - Build adj; dfs returns height; update ans with sum of two largest child heights

        Complexity: O(n) time/space.
        """
        if not edges:
            return 0
        adj = defaultdict(list)
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)
        ans = 0

        def dfs(u: int, parent: int) -> int:
            nonlocal ans
            top1 = top2 = 0
            for v in adj[u]:
                if v == parent:
                    continue
                h = dfs(v, u) + 1
                if h > top1:
                    top2, top1 = top1, h
                elif h > top2:
                    top2 = h
            ans = max(ans, top1 + top2)
            return top1

        dfs(0, -1)
        return ans
# @lc code=end
