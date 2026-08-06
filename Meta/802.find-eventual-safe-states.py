#
# @lc app=leetcode id=802 lang=python3
#
# [802] Find Eventual Safe States
#
# https://leetcode.com/problems/find-eventual-safe-states/description/
#
# algorithms
# Medium (70.66%)
# Likes:    7043
# Dislikes: 529
# Total Accepted:    571.8K
# Total Submissions: 809.2K
# Testcase Example:  '[[1,2],[2,3],[5],[0],[5],[],[]]'
#
# There is a directed graph of n nodes with each node labeled from 0 to n - 1.
# The graph is represented by a 0-indexed 2D integer array graph where graph[i]
# is an integer array of nodes adjacent to node i, meaning there is an edge
# from node i to each node in graph[i].
# 
# A node is a terminal node if there are no outgoing edges. A node is a safe
# node if every possible path starting from that node leads to a terminal node
# (or another safe node).
# 
# Return an array containing all the safe nodes of the graph. The answer should
# be sorted in ascending order.
# 
# 
# Example 1:
# 
# 
# Input: graph = [[1,2],[2,3],[5],[0],[5],[],[]]
# Output: [2,4,5,6]
# Explanation: The given graph is shown above.
# Nodes 5 and 6 are terminal nodes as there are no outgoing edges from either
# of them.
# Every path starting at nodes 2, 4, 5, and 6 all lead to either node 5 or 6.
# 
# Example 2:
# 
# 
# Input: graph = [[1,2,3,4],[1,2],[3,4],[0,4],[]]
# Output: [4]
# Explanation:
# Only node 4 is a terminal node, and every path starting at node 4 leads to
# node 4.
# 
# 
# 
# Constraints:
# 
# 
# n == graph.length
# 1 <= n <= 10^4
# 0 <= graph[i].length <= n
# 0 <= graph[i][j] <= n - 1
# graph[i] is sorted in a strictly increasing order.
# The graph may contain self-loops.
# The number of edges in the graph will be in the range [1, 4 * 10^4].
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def eventualSafeNodes(self, graph: List[List[int]]) -> List[int]:
        n = len(graph)
        color = [0] * n  # 0=unvisited, 1=visiting, 2=safe

        def dfs(node: int) -> bool:
            if color[node] != 0:
                return color[node] == 2
            color[node] = 1
            for nei in graph[node]:
                if not dfs(nei):
                    return False
            color[node] = 2
            return True

        return [i for i in range(n) if dfs(i)]
# @lc code=end

"""
Interview explanation:
A node is eventually safe if every path from it avoids cycles and ends at a terminal node. DFS with colors detects cycles: visiting a gray node means the current path found a cycle, so nodes depending on it are unsafe; nodes whose neighbors are all safe become safe.

Data structure: a color array stores DFS state and memoized safety.

Edge cases: terminal nodes have no outgoing edges, so they immediately become safe. Self-loops are detected as gray revisits and are unsafe.

Complexity: each node and edge is processed once, so O(V+E) time and O(V) space.
"""
