#
# @lc app=leetcode id=3203 lang=python3
#
# [3203] Find Minimum Diameter After Merging Two Trees
#
# https://leetcode.com/problems/find-minimum-diameter-after-merging-two-trees/description/
#
# algorithms
# Hard (57.02%)
# Likes:    710
# Dislikes: 40
# Total Accepted:    79.8K
# Total Submissions: 139.9K
# Testcase Example:  "[[0,1],[0,2],[0,3]]\n[[0,1]]"
#
#
# There exist two undirected trees with n and m nodes, numbered from 0 to
# n - 1 and from 0 to m - 1, respectively. You are given two 2D integer
# arrays edges1 and edges2 of lengths n - 1 and m - 1, respectively, where
# edges1[i] = [a_i, b_i] indicates that there is an edge between nodes a_i
# and b_i in the first tree and edges2[i] = [u_i, v_i] indicates that
# there is an edge between nodes u_i and v_i in the second tree.
#
# You must connect one node from the first tree with another node from the
# second tree with an edge.
#
# Return the minimum possible diameter of the resulting tree.
#
# The diameter of a tree is the length of the longest path between any two
# nodes in the tree.
#
# Example 1:
#
# Input: edges1 = [[0,1],[0,2],[0,3]], edges2 = [[0,1]]
#
# Output: 3
#
# Explanation:
#
# We can obtain a tree of diameter 3 by connecting node 0 from the first
# tree with any node from the second tree.
#
# Example 2:
#
# Input: edges1 = [[0,1],[0,2],[0,3],[2,4],[2,5],[3,6],[2,7]], edges2 =
# [[0,1],[0,2],[0,3],[2,4],[2,5],[3,6],[2,7]]
#
# Output: 5
#
# Explanation:
#
# We can obtain a tree of diameter 5 by connecting node 0 from the first
# tree with node 0 from the second tree.
#
# Constraints:
#
# 1 <= n, m <= 10^5
#
# edges1.length == n - 1
#
# edges2.length == m - 1
#
# edges1[i].length == edges2[i].length == 2
#
# edges1[i] = [a_i, b_i]
#
# 0 <= a_i, b_i < n
#
# edges2[i] = [u_i, v_i]
#
# 0 <= u_i, v_i < m
#
# The input is generated such that edges1 and edges2 represent valid
# trees.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def minimumDiameterAfterMerge(self, edges1: List[List[int]], edges2: List[List[int]]) -> int:
        """
        Interview explanation:
        Connect one node from each tree. The merged diameter is the max of each
        tree's diameter and the path that goes through the new edge, whose length
        is ceil(d1/2) + ceil(d2/2) + 1 when both ends are chosen as centers
        (minimum eccentricity / radius endpoints).

        Algorithm:
        - For each tree: build adjacency; two BFS (or DFS) to get diameter.
        - radius contribution = (diameter + 1) // 2.
        - Answer = max(d1, d2, r1 + r2 + 1).

        Complexity: O(n + m) time, O(n + m) space.
        """
        def diameter(edges: List[List[int]]) -> int:
            n = len(edges) + 1
            if n == 1:
                return 0
            g: List[List[int]] = [[] for _ in range(n)]
            for a, b in edges:
                g[a].append(b)
                g[b].append(a)

            def farthest(src: int) -> tuple[int, int]:
                dist = [-1] * n
                dist[src] = 0
                q = deque([src])
                far = src
                while q:
                    u = q.popleft()
                    if dist[u] > dist[far]:
                        far = u
                    for v in g[u]:
                        if dist[v] < 0:
                            dist[v] = dist[u] + 1
                            q.append(v)
                return far, dist[far]

            u, _ = farthest(0)
            _, d = farthest(u)
            return d

        d1 = diameter(edges1)
        d2 = diameter(edges2)
        return max(d1, d2, (d1 + 1) // 2 + (d2 + 1) // 2 + 1)
# @lc code=end
