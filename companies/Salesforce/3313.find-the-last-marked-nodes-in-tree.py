#
# @lc app=leetcode id=3313 lang=python3
#
# [3313] Find the Last Marked Nodes in Tree
#
# https://leetcode.com/problems/find-the-last-marked-nodes-in-tree/description/
#
# algorithms
# Hard (56.59%)
# Likes:    7
# Dislikes: 1
# Total Accepted:    691
# Total Submissions: 1.2K
# Testcase Example:  "[[0,1],[0,2]]"
#
#
# There exists an undirected tree with n nodes numbered 0 to n - 1. You
# are given a 2D integer array edges of length n - 1, where edges[i] =
# [u_i, v_i] indicates that there is an edge between nodes u_i and v_i in
# the tree.
#
# Initially, all nodes are unmarked. After every second, you mark all
# unmarked nodes which have at least one marked node adjacent to them.
#
# Return an array nodes where nodes[i] is the last node to get marked in
# the tree, if you mark node i at time t = 0. If nodes[i] has multiple
# answers for any node i, you can choose any one answer.
#
# Example 1:
#
# Input: edges = [[0,1],[0,2]]
#
# Output: [2,2,1]
#
# Explanation:
#
# For i = 0, the nodes are marked in the sequence: [0] -> [0,1,2]. Either
# 1 or 2 can be the answer.
#
# For i = 1, the nodes are marked in the sequence: [1] -> [0,1] ->
# [0,1,2]. Node 2 is marked last.
#
# For i = 2, the nodes are marked in the sequence: [2] -> [0,2] ->
# [0,1,2]. Node 1 is marked last.
#
# Example 2:
#
# Input: edges = [[0,1]]
#
# Output: [1,0]
#
# Explanation:
#
# For i = 0, the nodes are marked in the sequence: [0] -> [0,1].
#
# For i = 1, the nodes are marked in the sequence: [1] -> [0,1].
#
# Example 3:
#
# Input: edges = [[0,1],[0,2],[2,3],[2,4]]
#
# Output: [3,3,1,1,1]
#
# Explanation:
#
# For i = 0, the nodes are marked in the sequence: [0] -> [0,1,2] ->
# [0,1,2,3,4].
#
# For i = 1, the nodes are marked in the sequence: [1] -> [0,1] -> [0,1,2]
# -> [0,1,2,3,4].
#
# For i = 2, the nodes are marked in the sequence: [2] -> [0,2,3,4] ->
# [0,1,2,3,4].
#
# For i = 3, the nodes are marked in the sequence: [3] -> [2,3] ->
# [0,2,3,4] -> [0,1,2,3,4].
#
# For i = 4, the nodes are marked in the sequence: [4] -> [2,4] ->
# [0,2,3,4] -> [0,1,2,3,4].
#
# Constraints:
#
# 2 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i].length == 2
#
# 0 <= edges[i][0], edges[i][1] <= n - 1
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start
from typing import List


class Solution:
    def lastMarkedNodes(self, edges: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Marking spreads like multi-source BFS from a start. The last marked node
        is a farthest node; in a tree every farthest node is a diameter endpoint.

        Algorithm:
        - BFS from 0 to find diameter end u; BFS from u to find end v and dist_u.
        - BFS from v for dist_v. For each start s, answer the farther of u, v.

        Complexity: O(n) time, O(n) space.
        """
        n = len(edges) + 1
        adj: List[List[int]] = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        def bfs(root: int) -> tuple[list[int], int]:
            dist = [-1] * n
            dist[root] = 0
            q = [root]
            far = root
            for u in q:
                far = u
                for v in adj[u]:
                    if dist[v] == -1:
                        dist[v] = dist[u] + 1
                        q.append(v)
            return dist, far

        _, u = bfs(0)
        dist_u, v = bfs(u)
        dist_v, _ = bfs(v)
        return [u if dist_u[i] > dist_v[i] else v for i in range(n)]
# @lc code=end
