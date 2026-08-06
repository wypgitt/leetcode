#
# @lc app=leetcode id=3547 lang=python3
#
# [3547] Maximum Sum of Edge Values in a Graph
#
# https://leetcode.com/problems/maximum-sum-of-edge-values-in-a-graph/description/
#
# algorithms
# Hard (37.23%)
# Likes:    57
# Dislikes: 33
# Total Accepted:    7.3K
# Total Submissions: 19.5K
# Testcase Example:  "4\n[[0,1],[1,2],[2,3]]"
#
#
# You are given an undirected connected graph of n nodes, numbered from 0
# to n - 1. Each node is connected to at most 2 other nodes.
#
# The graph consists of m edges, represented by a 2D array edges, where
# edges[i] = [a_i, b_i] indicates that there is an edge between nodes a_i
# and b_i.
#
# You have to assign a unique value from 1 to n to each node. The value of
# an edge will be the product of the values assigned to the two nodes it
# connects.
#
# Your score is the sum of the values of all edges in the graph.
#
# Return the maximum score you can achieve.
#
# Example 1:
#
# Input: n = 4, edges = [[0,1],[1,2],[2,3]]
#
# Output: 23
#
# Explanation:
#
# The diagram above illustrates an optimal assignment of values to nodes.
# The sum of the values of the edges is: (1 * 3) + (3 * 4) + (4 * 2) = 23.
#
# Example 2:
#
# Input: n = 6, edges = [[0,3],[4,5],[2,0],[1,3],[2,4],[1,5]]
#
# Output: 82
#
# Explanation:
#
# The diagram above illustrates an optimal assignment of values to nodes.
# The sum of the values of the edges is: (1 * 2) + (2 * 4) + (4 * 6) + (6
# * 5) + (5 * 3) + (3 * 1) = 82.
#
# Constraints:
#
# 1 <= n <= 5 * 10^4
#
# m == edges.length
#
# 1 <= m <= n
#
# edges[i].length == 2
#
# 0 <= a_i, b_i < n
#
# a_i != b_i
#
# There are no repeated edges.
#
# The graph is connected.
#
# Each node is connected to at most 2 other nodes.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def maxScore(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Degree ≤ 2 ⇒ components are paths and cycles. Assign 1..n so large
        labels cluster on edges; give the largest remaining numbers to cycles
        first, then longer paths (isolates get leftovers and contribute 0).

        Algorithm:
        - Find components; classify cycle (all deg 2) vs path (size > 1).
        - For a block using values [left..right], build the optimal zigzag via a
          2-slot window (and close the cycle edge if needed).
        - Process all cycles, then paths by decreasing size.

        Complexity: O(n + m) time, O(n + m) space.
        """
        graph = [[] for _ in range(n)]
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)

        seen = set()
        cycle_sizes: List[int] = []
        path_sizes: List[int] = []

        def component(start: int) -> List[int]:
            comp = [start]
            seen.add(start)
            for u in comp:
                for v in graph[u]:
                    if v not in seen:
                        seen.add(v)
                        comp.append(v)
            return comp

        for i in range(n):
            if i in seen:
                continue
            comp = component(i)
            if all(len(graph[u]) == 2 for u in comp):
                cycle_sizes.append(len(comp))
            elif len(comp) > 1:
                path_sizes.append(len(comp))

        ans = 0
        cur_n = n
        for sz in cycle_sizes:
            ans += self._score(cur_n - sz + 1, cur_n, True)
            cur_n -= sz
        for sz in sorted(path_sizes, reverse=True):
            ans += self._score(cur_n - sz + 1, cur_n, False)
            cur_n -= sz
        return ans

    def _score(self, left: int, right: int, is_cycle: bool) -> int:
        window = deque([right, right])
        score = 0
        for value in range(right - 1, left - 1, -1):
            score += window.popleft() * value
            window.append(value)
        if is_cycle:
            score += window[0] * window[1]
        return score
# @lc code=end
