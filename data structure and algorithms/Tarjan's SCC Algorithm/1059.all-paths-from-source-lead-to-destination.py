#
# @lc app=leetcode id=1059 lang=python3
#
# [1059] All Paths from Source Lead to Destination
#
# https://leetcode.com/problems/all-paths-from-source-lead-to-destination/description/
#
# algorithms
# Medium (37.31%)
# Likes:    772
# Dislikes: 435
# Total Accepted:    77.9K
# Total Submissions: 208.8K
# Testcase Example:  "3\n[[0,1],[0,2]]\n0\n2"
#
#
# Given the edges of a directed graph where edges[i] = [a_i, b_i]
# indicates there is an edge between nodes a_i and b_i, and two nodes
# source and destination of this graph, determine whether or not all paths
# starting from source eventually, end at destination, that is:
#
# At least one path exists from the source node to the destination node
#
# If a path exists from the source node to a node with no outgoing edges,
# then that node is equal to destination.
#
# The number of possible paths from source to destination is a finite
# number.
#
# Return true if and only if all roads from source lead to destination.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[0,2]], source = 0, destination = 2
# Output: false
# Explanation: It is possible to reach and get stuck on both node 1 and
# node 2.
#
# Example 2:
#
# Input: n = 4, edges = [[0,1],[0,3],[1,2],[2,1]], source = 0, destination
# = 3
# Output: false
# Explanation: We have two possibilities: to end at node 3, or to loop
# over node 1 and node 2 indefinitely.
#
# Example 3:
#
# Input: n = 4, edges = [[0,1],[0,2],[1,3],[2,3]], source = 0, destination
# = 3
# Output: true
#
# Constraints:
#
# 1 <= n <= 10^4
#
# 0 <= edges.length <= 10^4
#
# edges.length == 2
#
# 0 <= a_i, b_i <= n - 1
#
# 0 <= source <= n - 1
#
# 0 <= destination <= n - 1
#
# The given graph may have self-loops and parallel edges.
#
# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def leadsToDestination(self, n: int, edges: List[List[int]], source: int, destination: int) -> bool:
        """
        Interview explanation:
        Premium. Every path from source must end at destination (no cycles on
        reachable paths; destination must be a sink). DFS with 3-color states:
        visiting (gray) detects cycle; black means fully validated.

        Algorithm:
        - Build adj; if destination has outgoing edges: False
        - dfs(u): if gray: cycle False; if black: True
          if no outs: return u==destination
          mark gray; all children dfs; mark black

        Complexity: O(n + e) time and space.
        """
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)
        if adj[destination]:
            return False
        WHITE, GRAY, BLACK = 0, 1, 2
        state = [WHITE] * n

        def dfs(u: int) -> bool:
            if state[u] == GRAY:
                return False
            if state[u] == BLACK:
                return True
            if not adj[u]:
                return u == destination
            state[u] = GRAY
            for v in adj[u]:
                if not dfs(v):
                    return False
            state[u] = BLACK
            return True

        return dfs(source)

    def leadsToDestination_memo(self, n: int, edges: List[List[int]], source: int, destination: int) -> bool:
        """
        Interview explanation:
        Alternate DFS with on-stack set for cycles and memo of success.

        Algorithm:
        - Same graph rules; memo[u]=whether all paths from u lead to dest

        Complexity: O(n + e) time and space.
        """
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
        if adj[destination]:
            return False
        memo = {}
        stack = set()

        def dfs(u: int) -> bool:
            if u in memo:
                return memo[u]
            if u in stack:
                return False
            if not adj[u]:
                memo[u] = u == destination
                return memo[u]
            stack.add(u)
            ok = all(dfs(v) for v in adj[u])
            stack.remove(u)
            memo[u] = ok
            return ok

        return dfs(source)
# @lc code=end
