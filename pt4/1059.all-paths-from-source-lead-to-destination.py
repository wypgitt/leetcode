#
# @lc app=leetcode id=1059 lang=python3
#
# [1059] All Paths from Source Lead to Destination
#
# https://leetcode.com/problems/all-paths-from-source-lead-to-destination/description/
#
# algorithms
# Medium (37.28%)
# Likes:    770
# Dislikes: 433
# Total Accepted:    76.9K
# Total Submissions: 206.3K
# Testcase Example:  '3\n[[0,1],[0,2]]\n0\n2'
#
# Given the edges of a directed graph where edges[i] = [ai, bi] indicates there
# is an edge between nodes ai and bi, and two nodes source and destination of
# this graph, determine whether or not all paths starting from source
# eventually, end at destination, that is:
# 
# 
# At least one path exists from the source node to the destination node
# If a path exists from the source node to a node with no outgoing edges, then
# that node is equal to destination.
# The number of possible paths from source to destination is a finite number.
# 
# 
# Return true if and only if all roads from source lead to destination.
# 
# 
# Example 1:
# 
# 
# Input: n = 3, edges = [[0,1],[0,2]], source = 0, destination = 2
# Output: false
# Explanation: It is possible to reach and get stuck on both node 1 and node
# 2.
# 
# 
# Example 2:
# 
# 
# Input: n = 4, edges = [[0,1],[0,3],[1,2],[2,1]], source = 0, destination = 3
# Output: false
# Explanation: We have two possibilities: to end at node 3, or to loop over
# node 1 and node 2 indefinitely.
# 
# 
# Example 3:
# 
# 
# Input: n = 4, edges = [[0,1],[0,2],[1,3],[2,3]], source = 0, destination = 3
# Output: true
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 10^4
# 0 <= edges.length <= 10^4
# edges.length == 2
# 0 <= ai, bi <= n - 1
# 0 <= source <= n - 1
# 0 <= destination <= n - 1
# The given graph may have self-loops and parallel edges.
# 
# 
#

# @lc code=start
import sys
from typing import List


class Solution:
    def leadsToDestination(self, n: int, edges: List[List[int]], source: int, destination: int) -> bool:
        sys.setrecursionlimit(max(1000, n + 10))

        graph = [[] for _ in range(n)]
        for start, end in edges:
            graph[start].append(end)

        state = [0] * n

        def dfs(node: int) -> bool:
            if not graph[node]:
                return node == destination

            if state[node] == 1:
                return False
            if state[node] == 2:
                return True

            state[node] = 1
            for neighbor in graph[node]:
                if not dfs(neighbor):
                    return False

            state[node] = 2
            return True

        return dfs(source)
# @lc code=end

"""
Interview Explanation

Core idea:
All paths from source must terminate at destination, and there must be only
finitely many such paths. A reachable dead end that is not destination fails.
A reachable cycle fails because it creates infinitely many paths or a path that
never ends.

Algorithm:
1. Build the directed adjacency list.
2. DFS from source using three states:
   - 0 = unvisited
   - 1 = currently visiting in this DFS path
   - 2 = already proven safe
3. If a node has no outgoing edges, it is valid only if it is destination.
4. If DFS reaches a visiting node, a reachable cycle exists, so return False.
5. A node is safe only if every outgoing neighbor is safe.

Data structure choice:
The adjacency list stores the graph compactly. The color/state array is the
standard structure for directed cycle detection plus memoized safety.

Correctness:
The terminal-node rule directly enforces that any path ending at a dead end
must end at destination. The visiting state detects cycles reachable from the
source, which violates the finite-path requirement. If all outgoing neighbors
of a node are safe, then every path starting from that node eventually reaches
destination; marking it safe memoizes that fact. DFS from source therefore
returns True exactly when all source paths lead to destination.

Complexity:
Each reachable node is fully processed once and each reachable edge is checked
once, so time is O(n + e). The graph and state arrays use O(n + e) space, and
the recursion stack can be O(n).

Tests and edge cases:
- Source has a path to a non-destination terminal node: False.
- Reachable cycle: False.
- Destination with outgoing edges: usually False unless all those paths still
  satisfy the same rules, and a self-loop is caught as a cycle.
- Source equals destination with no outgoing edges: True.
- Unreachable bad cycles do not matter because DFS starts at source.
"""
