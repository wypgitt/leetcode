#
# @lc app=leetcode id=2065 lang=python3
#
# [2065] Maximum Path Quality of a Graph
#
# https://leetcode.com/problems/maximum-path-quality-of-a-graph/description/
#
# algorithms
# Hard (62.69%)
# Likes:    741
# Dislikes: 53
# Total Accepted:    36.1K
# Total Submissions: 57.6K
# Testcase Example:  "[0,32,10,43]\n[[0,1,10],[1,2,15],[0,3,10]]\n49"
#
# There is an undirected graph with n nodes numbered from 0 to n - 1
# (inclusive). You are given a 0-indexed integer array values where values[i] is
# the value of the i^th node. You are also given a 0-indexed 2D integer array
# edges, where each edges[j] = [u_j, v_j, time_j] indicates that there is an
# undirected edge between the nodes u_j and v_j,_ and it takes time_j seconds to
# travel between the two nodes. Finally, you are given an integer maxTime.
#
# A valid path in the graph is any path that starts at node 0, ends at node 0,
# and takes at most maxTime seconds to complete. You may visit the same node
# multiple times. The quality of a valid path is the sum of the values of the
# unique nodes visited in the path (each node's value is added at most once to
# the sum).
#
# Return the maximum quality of a valid path.
#
# Note: There are at most four edges connected to each node.
#
#
#
# Example 1:
#
# Input: values = [0,32,10,43], edges = [[0,1,10],[1,2,15],[0,3,10]], maxTime =
# 49
# Output: 75
# Explanation:
# One possible path is 0 -> 1 -> 0 -> 3 -> 0. The total time taken is 10 + 10 +
# 10 + 10 = 40 <= 49.
# The nodes visited are 0, 1, and 3, giving a maximal path quality of 0 + 32 +
# 43 = 75.
#
# Example 2:
#
# Input: values = [5,10,15,20], edges = [[0,1,10],[1,2,10],[0,3,10]], maxTime =
# 30
# Output: 25
# Explanation:
# One possible path is 0 -> 3 -> 0. The total time taken is 10 + 10 = 20 <= 30.
# The nodes visited are 0 and 3, giving a maximal path quality of 5 + 20 = 25.
#
# Example 3:
#
# Input: values = [1,2,3,4], edges = [[0,1,10],[1,2,11],[2,3,12],[1,3,13]],
# maxTime = 50
# Output: 7
# Explanation:
# One possible path is 0 -> 1 -> 3 -> 1 -> 0. The total time taken is 10 + 13 +
# 13 + 10 = 46 <= 50.
# The nodes visited are 0, 1, and 3, giving a maximal path quality of 1 + 2 + 4
# = 7.
#
#
#
# Constraints:
#
#
# n == values.length
#
#
# 1 <= n <= 1000
#
#
# 0 <= values[i] <= 10^8
#
#
# 0 <= edges.length <= 2000
#
#
# edges[j].length == 3
#
#
# 0 <= u_j < v_j <= n - 1
#
#
# 10 <= time_j, maxTime <= 100
#
#
# All the pairs [u_j, v_j] are unique.
#
#
# There are at most four edges connected to each node.
#
#
# The graph may not be connected.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def maximalPathQuality(self, values: List[int], edges: List[List[int]], maxTime: int) -> int:
        """
        Interview explanation:
        Undirected weighted graph. Paths start and end at 0 within maxTime.
        Quality = sum of distinct node values on the path (revisits OK for
        edges/time, but value counted once). Maximize quality.

        Algorithm:
        - DFS from 0 tracking time used and visited-set for values; update ans
          whenever at 0; small degrees (≤4) keep search feasible.

        Complexity: exponential in path length; constrained by maxTime and degree.
        """
        g = defaultdict(list)
        for u, v, t in edges:
            g[u].append((v, t))
            g[v].append((u, t))
        n = len(values)
        ans = 0
        seen = [0] * n
        seen[0] = 1

        def dfs(u: int, time: int, quality: int):
            nonlocal ans
            if u == 0:
                ans = max(ans, quality)
            for v, w in g[u]:
                if time + w > maxTime:
                    continue
                first = seen[v] == 0
                seen[v] += 1
                dfs(v, time + w, quality + (values[v] if first else 0))
                seen[v] -= 1

        dfs(0, 0, values[0])
        return ans
# @lc code=end
