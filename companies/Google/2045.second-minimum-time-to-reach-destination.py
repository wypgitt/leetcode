#
# @lc app=leetcode id=2045 lang=python3
#
# [2045] Second Minimum Time to Reach Destination
#
# https://leetcode.com/problems/second-minimum-time-to-reach-destination/description/
#
# algorithms
# Hard (62.33%)
# Likes:    1354
# Dislikes: 70
# Total Accepted:    94.1K
# Total Submissions: 151K
# Testcase Example:  "5\n[[1,2],[1,3],[1,4],[3,4],[4,5]]\n3\n5"
#
# A city is represented as a bi-directional connected graph with n vertices
# where each vertex is labeled from 1 to n (inclusive). The edges in the graph
# are represented as a 2D integer array edges, where each edges[i] = [u_i, v_i]
# denotes a bi-directional edge between vertex u_i and vertex v_i. Every vertex
# pair is connected by at most one edge, and no vertex has an edge to itself.
# The time taken to traverse any edge is time minutes.
#
# Each vertex has a traffic signal which changes its color from green to red and
# vice versa every change minutes. All signals change at the same time. You can
# enter a vertex at any time, but can leave a vertex only when the signal is
# green. You cannot wait at a vertex if the signal is green.
#
# The second minimum value is defined as the smallest value strictly larger than
# the minimum value.
#
#
# For example the second minimum value of [2, 3, 4] is 3, and the second minimum
# value of [2, 2, 4] is 4.
#
# Given n, edges, time, and change, return the second minimum time it will take
# to go from vertex 1 to vertex n.
#
# Notes:
#
#
# You can go through any vertex any number of times, including 1 and n.
#
#
# You can assume that when the journey starts, all signals have just turned
# green.
#
#
#
# Example 1:
#
#
#
# Input: n = 5, edges = [[1,2],[1,3],[1,4],[3,4],[4,5]], time = 3, change = 5
# Output: 13
# Explanation:
# The figure on the left shows the given graph.
# The blue path in the figure on the right is the minimum time path.
# The time taken is:
# - Start at 1, time elapsed=0
# - 1 -> 4: 3 minutes, time elapsed=3
# - 4 -> 5: 3 minutes, time elapsed=6
# Hence the minimum time needed is 6 minutes.
#
# The red path shows the path to get the second minimum time.
# - Start at 1, time elapsed=0
# - 1 -> 3: 3 minutes, time elapsed=3
# - 3 -> 4: 3 minutes, time elapsed=6
# - Wait at 4 for 4 minutes, time elapsed=10
# - 4 -> 5: 3 minutes, time elapsed=13
# Hence the second minimum time is 13 minutes.
#
# Example 2:
#
# Input: n = 2, edges = [[1,2]], time = 3, change = 2
# Output: 11
# Explanation:
# The minimum time path is 1 -> 2 with time = 3 minutes.
# The second minimum time path is 1 -> 2 -> 1 -> 2 with time = 11 minutes.
#
#
#
# Constraints:
#
#
# 2 <= n <= 10^4
#
#
# n - 1 <= edges.length <= min(2 * 10^4, n * (n - 1) / 2)
#
#
# edges[i].length == 2
#
#
# 1 <= u_i, v_i <= n
#
#
# u_i != v_i
#
#
# There are no duplicate edges.
#
#
# Each vertex can be reached directly or indirectly from every other vertex.
#
#
# 1 <= time, change <= 10^3
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def secondMinimum(self, n: int, edges: List[List[int]], time: int, change: int) -> int:
        """
        Interview explanation:
        Undirected graph; travel each edge takes `time`; traffic light toggles
        every `change` minutes (green then red). Find second minimum arrival
        time at n (strictly greater than shortest).

        Algorithm:
        - BFS tracking first and second best arrival steps/distances (edge counts).
        - Need path with dist = shortest+1 or a longer simple detour; then simulate
          waiting for lights along that edge-count.

        Complexity: O(n+m) time, O(n+m) space.
        """
        g = defaultdict(list)
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        # dist1[i], dist2[i]: smallest and second smallest edge-counts to i
        d1 = [float('inf')] * (n + 1)
        d2 = [float('inf')] * (n + 1)
        d1[1] = 0
        q = deque([(1, 0)])  # node, steps
        while q:
            u, d = q.popleft()
            for v in g[u]:
                nd = d + 1
                if nd < d1[v]:
                    d2[v] = d1[v]
                    d1[v] = nd
                    q.append((v, nd))
                elif d1[v] < nd < d2[v]:
                    d2[v] = nd
                    q.append((v, nd))
        steps = d2[n]

        def arrival(steps: int) -> int:
            t = 0
            for _ in range(steps):
                # if in red period, wait until green
                # cycle 2*change: [0,change) green, [change,2*change) red
                if (t // change) % 2 == 1:
                    t = (t // change + 1) * change
                t += time
            return t

        return arrival(steps)
# @lc code=end
