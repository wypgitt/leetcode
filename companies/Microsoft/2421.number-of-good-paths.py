#
# @lc app=leetcode id=2421 lang=python3
#
# [2421] Number of Good Paths
#
# https://leetcode.com/problems/number-of-good-paths/description/
#
# algorithms
# Hard (56.51%)
# Likes:    2498
# Dislikes: 115
# Total Accepted:    67.5K
# Total Submissions: 119.5K
# Testcase Example:  "[1,3,2,1,3]\n[[0,1],[0,2],[2,3],[2,4]]"
#
# There is a tree (i.e. a connected, undirected graph with no cycles) consisting
# of n nodes numbered from 0 to n - 1 and exactly n - 1 edges.
#
# You are given a 0-indexed integer array vals of length n where vals[i] denotes
# the value of the i^th node. You are also given a 2D integer array edges where
# edges[i] = [a_i, b_i] denotes that there exists an undirected edge connecting
# nodes a_i and b_i.
#
# A good path is a simple path that satisfies the following conditions:
#
#
# The starting node and the ending node have the same value.
#
#
# All nodes between the starting node and the ending node have values less than
# or equal to the starting node (i.e. the starting node's value should be the
# maximum value along the path).
#
# Return the number of distinct good paths.
#
# Note that a path and its reverse are counted as the same path. For example, 0
# -> 1 is considered to be the same as 1 -> 0. A single node is also considered
# as a valid path.
#
#
#
# Example 1:
#
# Input: vals = [1,3,2,1,3], edges = [[0,1],[0,2],[2,3],[2,4]]
# Output: 6
# Explanation: There are 5 good paths consisting of a single node.
# There is 1 additional good path: 1 -> 0 -> 2 -> 4.
# (The reverse path 4 -> 2 -> 0 -> 1 is treated as the same as 1 -> 0 -> 2 ->
# 4.)
# Note that 0 -> 2 -> 3 is not a good path because vals[2] > vals[0].
#
# Example 2:
#
# Input: vals = [1,1,2,2,3], edges = [[0,1],[1,2],[2,3],[2,4]]
# Output: 7
# Explanation: There are 5 good paths consisting of a single node.
# There are 2 additional good paths: 0 -> 1 and 2 -> 3.
#
# Example 3:
#
# Input: vals = [1], edges = []
# Output: 1
# Explanation: The tree consists of only one node, so there is one good path.
#
#
#
# Constraints:
#
#
# n == vals.length
#
#
# 1 <= n <= 3 * 10^4
#
#
# 0 <= vals[i] <= 10^5
#
#
# edges.length == n - 1
#
#
# edges[i].length == 2
#
#
# 0 <= a_i, b_i < n
#
#
# a_i != b_i
#
#
# edges represents a valid tree.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def numberOfGoodPaths(self, vals: List[int], edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Good path: endpoints equal value v and all nodes on path have value <= v.
        Count good paths (single nodes count).

        Algorithm:
        - Union-Find nodes in increasing value order; for each value, connect via
          edges to smaller/equal neighbors already active; count pairs within same
          component among nodes of that value: C(sz,2)+sz.

        Complexity: O(n α(n) + n log n) time, O(n) space.
        """
        n = len(vals)
        parent = list(range(n))
        size = [1] * n

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if size[ra] < size[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            size[ra] += size[rb]

        graph = defaultdict(list)
        for a, b in edges:
            graph[a].append(b)
            graph[b].append(a)

        val_nodes = defaultdict(list)
        for i, v in enumerate(vals):
            val_nodes[v].append(i)

        ans = 0
        for v in sorted(val_nodes):
            nodes = val_nodes[v]
            for u in nodes:
                for nei in graph[u]:
                    if vals[nei] <= v:
                        union(u, nei)
            groups = defaultdict(int)
            for u in nodes:
                groups[find(u)] += 1
            for c in groups.values():
                ans += c * (c + 1) // 2
        return ans
# @lc code=end
