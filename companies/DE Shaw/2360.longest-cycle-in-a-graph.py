#
# @lc app=leetcode id=2360 lang=python3
#
# [2360] Longest Cycle in a Graph
#
# https://leetcode.com/problems/longest-cycle-in-a-graph/description/
#
# algorithms
# Hard (51.02%)
# Likes:    2592
# Dislikes: 53
# Total Accepted:    113K
# Total Submissions: 221.5K
# Testcase Example:  "[3,3,4,2,3]"
#
# You are given a directed graph of n nodes numbered from 0 to n - 1, where each
# node has at most one outgoing edge.
#
# The graph is represented with a given 0-indexed array edges of size n,
# indicating that there is a directed edge from node i to node edges[i]. If
# there is no outgoing edge from node i, then edges[i] == -1.
#
# Return the length of the longest cycle in the graph. If no cycle exists,
# return -1.
#
# A cycle is a path that starts and ends at the same node.
#
#
#
# Example 1:
#
# Input: edges = [3,3,4,2,3]
# Output: 3
# Explanation: The longest cycle in the graph is the cycle: 2 -> 4 -> 3 -> 2.
# The length of this cycle is 3, so 3 is returned.
#
# Example 2:
#
# Input: edges = [2,-1,3,1]
# Output: -1
# Explanation: There are no cycles in this graph.
#
#
#
# Constraints:
#
#
# n == edges.length
#
#
# 2 <= n <= 10^5
#
#
# -1 <= edges[i] < n
#
#
# edges[i] != i
#

# @lc code=start

from typing import List


class Solution:
    def longestCycle(self, edges: List[int]) -> int:
        """
        Interview explanation:
        Directed graph outdegree <=1. Return length of longest cycle, or -1.

        Algorithm:
        - DFS with time stamps: enter time per node; if revisit in current path,
          cycle length = time - enter[node].

        Complexity: O(n) time, O(n) space.
        """
        n = len(edges)
        time = [0] * n
        clock = 1
        ans = -1
        for i in range(n):
            if time[i]:
                continue
            start = clock
            u = i
            while u != -1 and time[u] == 0:
                time[u] = clock
                clock += 1
                u = edges[u]
            if u != -1 and time[u] >= start:
                ans = max(ans, clock - time[u])
        return ans

    def longestCycle_dfs(self, edges: List[int]) -> int:
        """
        Interview explanation:
        Alternate: color DFS (0/1/2) to detect cycles and measure path length.

        Algorithm:
        - White/gray/black; on gray back-edge compute cycle length along path.

        Complexity: O(n) time, O(n) space.
        """
        n = len(edges)
        color = [0] * n
        dist = [0] * n
        ans = -1

        def dfs(u: int) -> None:
            nonlocal ans
            color[u] = 1
            v = edges[u]
            if v != -1:
                if color[v] == 0:
                    dist[v] = dist[u] + 1
                    dfs(v)
                elif color[v] == 1:
                    ans = max(ans, dist[u] - dist[v] + 1)
            color[u] = 2

        for i in range(n):
            if color[i] == 0:
                dfs(i)
        return ans
# @lc code=end
