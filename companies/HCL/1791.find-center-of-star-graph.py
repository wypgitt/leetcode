#
# @lc app=leetcode id=1791 lang=python3
#
# [1791] Find Center of Star Graph
#
# https://leetcode.com/problems/find-center-of-star-graph/description/
#
# algorithms
# Easy (86.6%)
# Likes:    2020
# Dislikes: 184
# Total Accepted:    462K
# Total Submissions: 534K
# Testcase Example:  "[[1,2],[2,3],[4,2]]"
#
# There is an undirected star graph consisting of n nodes labeled from 1 to n.
# A star graph is a graph where there is one center node and exactly n - 1
# edges that connect the center node with every other node.
#
# You are given a 2D integer array edges where each edges[i] = [u_i, v_i]
# indicates that there is an edge between the nodes u_i and v_i. Return the
# center of the given star graph.
#
# Example 1:
#
# Input: edges = [[1,2],[2,3],[4,2]]
# Output: 2
# Explanation: As shown in the figure above, node 2 is connected to every other
# node, so 2 is the center.
#
# Example 2:
#
# Input: edges = [[1,2],[5,1],[1,3],[1,4]]
# Output: 1
#
# Constraints:
#
# 3 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i].length == 2
#
# 1 <= u_i, v_i <= n
#
# u_i != v_i
#
# The given edges represent a valid star graph.
#

# @lc code=start
from typing import List


class Solution:
    def findCenter(self, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Star graph: one center connected to all others. The center appears in
        every edge → intersection of the first two edges.

        Algorithm:
        - a,b = edges[0]; return a if a in edges[1] else b.

        Complexity: O(1) time, O(1) space.
        """
        a, b = edges[0]
        return a if a in edges[1] else b

    def findCenter_degree(self, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: count degrees; center has degree n-1 = len(edges).

        Algorithm:
        - Counter endpoints; return node with count == len(edges).

        Complexity: O(n) time, O(n) space.
        """
        from collections import Counter
        c = Counter()
        for u, v in edges:
            c[u] += 1
            c[v] += 1
        n_edges = len(edges)
        for node, d in c.items():
            if d == n_edges:
                return node
        return -1
# @lc code=end
