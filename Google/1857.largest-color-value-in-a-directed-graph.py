#
# @lc app=leetcode id=1857 lang=python3
#
# [1857] Largest Color Value in a Directed Graph
#
# https://leetcode.com/problems/largest-color-value-in-a-directed-graph/description/
#
# algorithms
# Hard (57.19%)
# Likes:    2668
# Dislikes: 87
# Total Accepted:    154K
# Total Submissions: 269K
# Testcase Example:  "\"abaca\""
#
# There is a directed graph of n colored nodes and m edges. The nodes are
# numbered from 0 to n - 1.
#
# You are given a string colors where colors[i] is a lowercase English letter
# representing the color of the i^th node in this graph (0-indexed). You are
# also given a 2D array edges where edges[j] = [a_j, b_j] indicates that there
# is a directed edge from node a_j to node b_j.
#
# A valid path in the graph is a sequence of nodes x_1 -> x_2 -> x_3 -> ... ->
# x_k such that there is a directed edge from x_i to x_i+1 for every 1 <= i <
# k. The color value of the path is the number of nodes that are colored the
# most frequently occurring color along that path.
#
# Return the largest color value of any valid path in the given graph, or -1 if
# the graph contains a cycle.
#
# Example 1:
#
# Input: colors = "abaca", edges = [[0,1],[0,2],[2,3],[3,4]]
# Output: 3
# Explanation: The path 0 -> 2 -> 3 -> 4 contains 3 nodes that are colored "a"
# (red in the above image).
#
# Example 2:
#
# Input: colors = "a", edges = [[0,0]]
# Output: -1
# Explanation: There is a cycle from 0 to 0.
#
# Constraints:
#
# n == colors.length
#
# m == edges.length
#
# 1 <= n <= 10^5
#
# 0 <= m <= 10^5
#
# colors consists of lowercase English letters.
#
# 0 <= a_j, b_j < n
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def largestPathValue(self, colors: str, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Directed graph; maximize max frequency of any single color along a path.
        Detect cycles → -1. Topological DP: for each node keep best color counts
        reachable ending at that node.

        Algorithm (topo + DP):
        - Build adj/indegree; dp[u][26] color counts.
        - Kahn: for each u, dp[u][colors[u]]++; push neighbors updating max counts.
        - If processed < n: cycle → -1; else max over dp.

        Complexity: O(n+m) time (alphabet 26), O(n+m) space.
        """
        n = len(colors)
        adj = [[] for _ in range(n)]
        indeg = [0] * n
        for u, v in edges:
            adj[u].append(v)
            indeg[v] += 1
        dp = [[0] * 26 for _ in range(n)]
        q = deque(i for i in range(n) if indeg[i] == 0)
        seen = 0
        ans = 0
        while q:
            u = q.popleft()
            seen += 1
            c = ord(colors[u]) - 97
            dp[u][c] += 1
            ans = max(ans, dp[u][c])
            for v in adj[u]:
                for k in range(26):
                    if dp[u][k] > dp[v][k]:
                        dp[v][k] = dp[u][k]
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        return ans if seen == n else -1

    def largestPathValue_dfs(self, colors: str, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: DFS with memoized color-count vectors; 3-color cycle detect.

        Algorithm:
        - state 0/1/2; dfs returns best counts array or signals cycle.
        - On finish, add own color; ans = global max.

        Complexity: O(n+m) time, O(n) space.
        """
        n = len(colors)
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
        memo = [None] * n
        state = [0] * n
        ans = 0
        cycle = False

        def dfs(u: int):
            nonlocal ans, cycle
            if state[u] == 1:
                cycle = True
                return None
            if state[u] == 2:
                return memo[u]
            state[u] = 1
            cur = [0] * 26
            for v in adj[u]:
                res = dfs(v)
                if cycle:
                    return None
                for k in range(26):
                    if res[k] > cur[k]:
                        cur[k] = res[k]
            cur[ord(colors[u]) - 97] += 1
            ans = max(ans, max(cur))
            state[u] = 2
            memo[u] = cur
            return cur

        for i in range(n):
            if state[i] == 0:
                dfs(i)
                if cycle:
                    return -1
        return ans
# @lc code=end
