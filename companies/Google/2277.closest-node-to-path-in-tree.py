#
# @lc app=leetcode id=2277 lang=python3
#
# [2277] Closest Node to Path in Tree
#
# https://leetcode.com/problems/closest-node-to-path-in-tree/description/
#
# algorithms
# Hard (62.57%)
# Likes:    143
# Dislikes: 3
# Total Accepted:    6.9K
# Total Submissions: 11K
# Testcase Example:  "7\n[[0,1],[0,2],[0,3],[1,4],[2,5],[2,6]]\n[[5,3,4],[5,3,6]]"
#
#
# You are given a positive integer n representing the number of nodes in a
# tree, numbered from 0 to n - 1 (inclusive). You are also given a 2D
# integer array edges of length n - 1, where edges[i] = [node1_i, node2_i]
# denotes that there is a bidirectional edge connecting node1_i and
# node2_i in the tree.
#
# You are given a 0-indexed integer array query of length m where query[i]
# = [start_i, end_i, node_i] means that for the i^th query, you are tasked
# with finding the node on the path from start_i to end_i that is closest
# to node_i.
#
# Return an integer array answer of length m, where answer[i] is the
# answer to the i^th query.
#
# Example 1:
#
# Input: n = 7, edges = [[0,1],[0,2],[0,3],[1,4],[2,5],[2,6]], query =
# [[5,3,4],[5,3,6]]
# Output: [0,2]
# Explanation:
# The path from node 5 to node 3 consists of the nodes 5, 2, 0, and 3.
# The distance between node 4 and node 0 is 2.
# Node 0 is the node on the path closest to node 4, so the answer to the
# first query is 0.
# The distance between node 6 and node 2 is 1.
# Node 2 is the node on the path closest to node 6, so the answer to the
# second query is 2.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1],[1,2]], query = [[0,1,2]]
# Output: [1]
# Explanation:
# The path from node 0 to node 1 consists of the nodes 0, 1.
# The distance between node 2 and node 1 is 1.
# Node 1 is the node on the path closest to node 2, so the answer to the
# first query is 1.
#
# Example 3:
#
# Input: n = 3, edges = [[0,1],[1,2]], query = [[0,0,0]]
# Output: [0]
# Explanation:
# The path from node 0 to node 0 consists of the node 0.
# Since 0 is the only node on the path, the answer to the first query is
# 0.
#
# Constraints:
#
# 1 <= n <= 1000
#
# edges.length == n - 1
#
# edges[i].length == 2
#
# 0 <= node1_i, node2_i <= n - 1
#
# node1_i != node2_i
#
# 1 <= query.length <= 1000
#
# query[i].length == 3
#
# 0 <= start_i, end_i, node_i <= n - 1
#
# The graph is a tree.
#
# @lc code=start
from typing import List


class Solution:
    def closestNode(self, n: int, edges: List[List[int]], query: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Tree queries: for path(start,end), find node on that path closest to node.

        Algorithm:
        - Precompute all-pairs distances via DFS from each node (n<=1000).
        - Walk path from start toward end; keep vertex minimizing dist to target.

        Complexity: O(n^2 + q*n) time, O(n^2) space.
        """
        tree = [[] for _ in range(n)]
        for u, v in edges:
            tree[u].append(v)
            tree[v].append(u)
        dist = [[-1] * n for _ in range(n)]

        def fill(start: int, u: int, d: int) -> None:
            dist[start][u] = d
            for v in tree[u]:
                if dist[start][v] == -1:
                    fill(start, v, d + 1)

        for i in range(n):
            fill(i, i, 0)

        def find_closest(u: int, end: int, node: int, ans: int) -> int:
            for v in tree[u]:
                if dist[v][end] < dist[u][end]:
                    nxt = ans if dist[ans][node] < dist[v][node] else v
                    return find_closest(v, end, node, nxt)
            return ans

        return [find_closest(s, e, node, s) for s, e, node in query]

    def closestNode_bfs(self, n: int, edges: List[List[int]], query: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Per-query BFS alternate: get path then BFS from node to path set.

        Algorithm:
        - BFS parents for path; BFS from node until hit path.

        Complexity: O(q * n) time, O(n) space.
        """
        from collections import deque
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)

        def path_nodes(a: int, b: int):
            parent = [-1] * n
            parent[a] = a
            dq = deque([a])
            while dq:
                u = dq.popleft()
                if u == b:
                    break
                for v in g[u]:
                    if parent[v] == -1:
                        parent[v] = u
                        dq.append(v)
            nodes = set()
            cur = b
            while True:
                nodes.add(cur)
                if cur == a:
                    break
                cur = parent[cur]
            return nodes

        ans = []
        for s, e, node in query:
            nodes = path_nodes(s, e)
            if node in nodes:
                ans.append(node)
                continue
            dq = deque([node])
            seen = {node}
            found = node
            while dq:
                u = dq.popleft()
                if u in nodes:
                    found = u
                    break
                for v in g[u]:
                    if v not in seen:
                        seen.add(v)
                        dq.append(v)
            ans.append(found)
        return ans
# @lc code=end
