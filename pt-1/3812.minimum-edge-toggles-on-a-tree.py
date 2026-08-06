#
# @lc app=leetcode id=3812 lang=python3
#
# [3812] Minimum Edge Toggles on a Tree
#
# https://leetcode.com/problems/minimum-edge-toggles-on-a-tree/description/
#
# algorithms
# Hard (65.63%)
# Likes:    53
# Dislikes: 5
# Total Accepted:    6.7K
# Total Submissions: 10.2K
# Testcase Example:  "3\n[[0,1],[1,2]]\n\"010\"\n\"100\""
#
#
# You are given an undirected tree with n nodes, numbered from 0 to n - 1.
# It is represented by a 2D integer array edges​​​​​​​ of length n - 1,
# where edges[i] = [a_i, b_i] indicates that there is an edge between
# nodes a_i and b_i in the tree.
#
# You are also given two binary strings start and target of length n. For
# each node x, start[x] is its initial color and target[x] is its desired
# color.
#
# In one operation, you may pick an edge with index i and toggle both of
# its endpoints. That is, if the edge is [u, v], then the colors of nodes
# u and v each flip from '0' to '1' or from '1' to '0'.
#
# Return an array of edge indices whose operations transform start into
# target. Among all valid sequences with minimum possible length, return
# the edge indices in increasing​​​​​​​ order.
#
# If it is impossible to transform start into target, return an array
# containing a single element equal to -1.
#
# Example 1:
#
# ​​​​​​​
#
# Input: n = 3, edges = [[0,1],[1,2]], start = "010", target = "100"
#
# Output: [0]
#
# Explanation:
#
# Toggle edge with index 0, which flips nodes 0 and 1.
#
# ​​​​​​​The string changes from "010" to "100", matching the target.
#
# Example 2:
#
# Input: n = 7, edges = [[0,1],[1,2],[2,3],[3,4],[3,5],[1,6]], start =
# "0011000", target = "0010001"
#
# Output: [1,2,5]
#
# Explanation:
#
# Toggle edge with index 1, which flips nodes 1 and 2.
#
# Toggle edge with index 2, which flips nodes 2 and 3.
#
# Toggle edge with index 5, which flips nodes 1 and 6.
#
# After these operations, the resulting string becomes "0010001", which
# matches the target.
#
# Example 3:
#
# ​​​​​​​
#
# Input: n = 2, edges = [[0,1]], start = "00", target = "01"
#
# Output: [-1]
#
# Explanation:
#
# There is no sequence of edge toggles that transforms "00" into "01".
# Therefore, we return [-1].
#
# Constraints:
#
# 2 <= n == start.length == target.length <= 10^5
#
# edges.length == n - 1
#
# edges[i] = [a_i, b_i]
#
# 0 <= a_i, b_i < n
#
# start[i] is either '0' or '1'.
#
# target[i] is either '0' or '1'.
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start
from typing import List


class Solution:
    def minimumFlips(
        self, n: int, edges: List[List[int]], start: str, target: str
    ) -> List[int]:
        """
        Interview explanation:
        Each edge toggle flips both endpoints. Find a minimum set of edges whose
        toggles turn start into target; return sorted indices, or [-1].

        Algorithm:
        - Root the tree at 0; compute need[x] = start[x] XOR target[x].
        - Process leaves upward: if need[node] is 1, must toggle the parent edge,
          which flips need[node] and need[parent].
        - If root still needs a flip, impossible.

        Complexity: O(n log n) time (sort answer), O(n) space.
        """
        graph = [[] for _ in range(n)]
        for idx, (u, v) in enumerate(edges):
            graph[u].append((v, idx))
            graph[v].append((u, idx))

        parent = [-1] * n
        parent_edge = [-1] * n
        order = [0]

        for node in order:
            for nei, edge_idx in graph[node]:
                if nei == parent[node]:
                    continue
                parent[nei] = node
                parent_edge[nei] = edge_idx
                order.append(nei)

        need = [int(a != b) for a, b in zip(start, target)]
        answer = []

        for node in reversed(order[1:]):
            if need[node]:
                answer.append(parent_edge[node])
                need[node] ^= 1
                need[parent[node]] ^= 1

        if need[0]:
            return [-1]

        answer.sort()
        return answer
# @lc code=end
