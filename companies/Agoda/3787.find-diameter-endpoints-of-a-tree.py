#
# @lc app=leetcode id=3787 lang=python3
#
# [3787] Find Diameter Endpoints of a Tree
#
# https://leetcode.com/problems/find-diameter-endpoints-of-a-tree/description/
#
# algorithms
# Medium (65.56%)
# Likes:    6
# Dislikes: 2
# Total Accepted:    769
# Total Submissions: 1.2K
# Testcase Example:  "3\n[[0,1],[1,2]]"
#
#
# You are given an undirected tree with n nodes, numbered from 0 to n - 1.
# It is represented by a 2D integer array edges​​​​​​​ of length n - 1,
# where edges[i] = [a_i, b_i] indicates that there is an edge between
# nodes a_i and b_i in the tree.
#
# A node is called special if it is an endpoint of any diameter path of
# the tree.
#
# Return a binary string s of length n, where s[i] = '1' if node i is
# special, and s[i] = '0' otherwise.
#
# A diameter path of a tree is the longest simple path between any two
# nodes. A tree may have multiple diameter paths.
#
# An endpoint of a path is the first or last node on that path.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[1,2]]
#
# Output: "101"
#
# Explanation:
#
# The diameter of this tree consists of 2 edges.
#
# The only diameter path is the path from node 0 to node 2
#
# The endpoints of this path are nodes 0 and 2, so they are special.
#
# Example 2:
#
# Input: n = 7, edges = [[0,1],[1,2],[2,3],[3,4],[3,5],[1,6]]
#
# Output: "1000111"
#
# Explanation:
#
# The diameter of this tree consists of 4 edges. There are 4 diameter
# paths:
#
# The path from node 0 to node 4
#
# The path from node 0 to node 5
#
# The path from node 6 to node 4
#
# The path from node 6 to node 5
#
# The special nodes are nodes 0, 4, 5, 6, as they are endpoints in at
# least one diameter path.
#
# Example 3:
#
# ​​​​​​​
#
# Input: n = 2, edges = [[0,1]]
#
# Output: "11"
#
# Explanation:
#
# The diameter of this tree consists of 1 edge.
#
# The only diameter path is the path from node 0 to node 1
#
# The endpoints of this path are nodes 0 and 1, so they are special.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i] = [a_i, b_i]
#
# 0 <= a_i, b_i < n
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def findSpecialNodes(self, n: int, edges: List[List[int]]) -> str:
        """
        Interview explanation:
        Diameter endpoints are exactly the nodes at maximum distance from one
        diameter end, and those at maximum distance from the other end.

        Algorithm:
        - BFS from 0 -> farthest set A (one diameter side).
        - BFS from any a in A -> farthest set B (other side).
        - Mark all nodes in A ∪ B as '1'.

        Complexity: O(n) time, O(n) space.
        """
        adj: List[List[int]] = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        def farthest_layer(src: int) -> List[int]:
            dist = [-1] * n
            dist[src] = 0
            q = deque([src])
            last: List[int] = [src]
            while q:
                last = list(q)
                for _ in range(len(q)):
                    u = q.popleft()
                    for v in adj[u]:
                        if dist[v] < 0:
                            dist[v] = dist[u] + 1
                            q.append(v)
            # all nodes in the last BFS layer share the max distance
            maxd = dist[last[0]]
            return [u for u in range(n) if dist[u] == maxd]

        side_a = farthest_layer(0)
        side_b = farthest_layer(side_a[0])
        special = set(side_a) | set(side_b)
        return "".join("1" if i in special else "0" for i in range(n))
# @lc code=end
