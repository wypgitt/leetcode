#
# @lc app=leetcode id=2493 lang=python3
#
# [2493] Divide Nodes Into the Maximum Number of Groups
#
# https://leetcode.com/problems/divide-nodes-into-the-maximum-number-of-groups/description/
#
# algorithms
# Hard (66.86%)
# Likes:    1016
# Dislikes: 76
# Total Accepted:    87.7K
# Total Submissions: 131.2K
# Testcase Example:  "6\n[[1,2],[1,4],[1,5],[2,6],[2,3],[4,6]]"
#
# You are given a positive integer n representing the number of nodes in an
# undirected graph. The nodes are labeled from 1 to n.
#
# You are also given a 2D integer array edges, where edges[i] = [a_i, b_i]
# indicates that there is a bidirectional edge between nodes a_i and b_i. Notice
# that the given graph may be disconnected.
#
# Divide the nodes of the graph into m groups (1-indexed) such that:
#
#
# Each node in the graph belongs to exactly one group.
#
#
# For every pair of nodes in the graph that are connected by an edge [a_i, b_i],
# if a_i belongs to the group with index x, and b_i belongs to the group with
# index y, then |y - x| = 1.
#
# Return the maximum number of groups (i.e., maximum m) into which you can
# divide the nodes. Return -1 if it is impossible to group the nodes with the
# given conditions.
#
#
#
# Example 1:
#
# Input: n = 6, edges = [[1,2],[1,4],[1,5],[2,6],[2,3],[4,6]]
# Output: 4
# Explanation: As shown in the image we:
# - Add node 5 to the first group.
# - Add node 1 to the second group.
# - Add nodes 2 and 4 to the third group.
# - Add nodes 3 and 6 to the fourth group.
# We can see that every edge is satisfied.
# It can be shown that that if we create a fifth group and move any node from
# the third or fourth group to it, at least on of the edges will not be
# satisfied.
#
# Example 2:
#
# Input: n = 3, edges = [[1,2],[2,3],[3,1]]
# Output: -1
# Explanation: If we add node 1 to the first group, node 2 to the second group,
# and node 3 to the third group to satisfy the first two edges, we can see that
# the third edge will not be satisfied.
# It can be shown that no grouping is possible.
#
#
#
# Constraints:
#
#
# 1 <= n <= 500
#
#
# 1 <= edges.length <= 10^4
#
#
# edges[i].length == 2
#
#
# 1 <= a_i, b_i <= n
#
#
# a_i != b_i
#
#
# There is at most one edge between any pair of vertices.
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def magnificentSets(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Partition connected components into most groups such that edges only
        join consecutive groups (graph distance layering). Impossible if not
        bipartite.

        Algorithm:
        - For each component, verify bipartite; for each start, BFS layers;
          take max depth; sum over components.

        Complexity: O(n*(n+m)) time, O(n+m) space.
        """
        g = defaultdict(list)
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)

        color = [0] * (n + 1)

        def bipartite_component(start: int):
            nodes = []
            q = deque([start])
            color[start] = 1
            while q:
                u = q.popleft()
                nodes.append(u)
                for v in g[u]:
                    if color[v] == 0:
                        color[v] = -color[u]
                        q.append(v)
                    elif color[v] == color[u]:
                        return None
            return nodes

        def max_groups(nodes: List[int]) -> int:
            best = 0
            for src in nodes:
                dist = {src: 1}
                q = deque([src])
                while q:
                    u = q.popleft()
                    for v in g[u]:
                        if v not in dist:
                            dist[v] = dist[u] + 1
                            q.append(v)
                best = max(best, max(dist.values()))
            return best

        ans = 0
        for i in range(1, n + 1):
            if color[i] == 0:
                nodes = bipartite_component(i)
                if nodes is None:
                    return -1
                ans += max_groups(nodes)
        return ans
# @lc code=end

