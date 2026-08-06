#
# @lc app=leetcode id=3311 lang=python3
#
# [3311] Construct 2D Grid Matching Graph Layout
#
# https://leetcode.com/problems/construct-2d-grid-matching-graph-layout/description/
#
# algorithms
# Hard (30.36%)
# Likes:    85
# Dislikes: 12
# Total Accepted:    4.8K
# Total Submissions: 15.8K
# Testcase Example:  "4\n[[0,1],[0,2],[1,3],[2,3]]"
#
#
# You are given a 2D integer array edges representing an undirected graph
# having n nodes, where edges[i] = [u_i, v_i] denotes an edge between
# nodes u_i and v_i.
#
# Construct a 2D grid that satisfies these conditions:
#
# The grid contains all nodes from 0 to n - 1 in its cells, with each node
# appearing exactly once.
#
# Two nodes should be in adjacent grid cells (horizontally or vertically)
# if and only if there is an edge between them in edges.
#
# It is guaranteed that edges can form a 2D grid that satisfies the
# conditions.
#
# Return a 2D integer array satisfying the conditions above. If there are
# multiple solutions, return any of them.
#
# Example 1:
#
# Input: n = 4, edges = [[0,1],[0,2],[1,3],[2,3]]
#
# Output: [[3,1],[2,0]]
#
# Explanation:
#
# Example 2:
#
# Input: n = 5, edges = [[0,1],[1,3],[2,3],[2,4]]
#
# Output: [[4,2,3,1,0]]
#
# Explanation:
#
# Example 3:
#
# Input: n = 9, edges =
# [[0,1],[0,4],[0,5],[1,7],[2,3],[2,4],[2,5],[3,6],[4,6],[4,7],[6,8],[7,8]]
#
# Output: [[8,6,3],[7,4,2],[1,0,5]]
#
# Explanation:
#
# Constraints:
#
# 2 <= n <= 5 * 10^4
#
# 1 <= edges.length <= 10^5
#
# edges[i] = [u_i, v_i]
#
# 0 <= u_i < v_i < n
#
# All the edges are distinct.
#
# The input is generated such that edges can form a 2D grid that satisfies
# the conditions.
#

# @lc code=start
from typing import List


class Solution:
    def constructGridLayout(self, n: int, edges: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        The graph is a grid graph. Corners have minimal degree; rebuild the grid
        by recovering the first row from a corner, then dropping row by row.

        Algorithm:
        - Pick a min-degree corner. Grow the first row along boundary degrees
          (cornerDegree or cornerDegree+1) preferring smaller degrees.
        - For each later row, each cell is the unseen neighbor of the cell above.

        Complexity: O(n log d) time from neighbor sorts, O(n) space.
        """
        graph: List[List[int]] = [[] for _ in range(n)]
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)

        corner = min(range(n), key=lambda x: len(graph[x]))
        seen = {corner}
        corner_deg = len(graph[corner])
        row = [corner]
        while len(row) == 1 or len(graph[row[-1]]) == corner_deg + 1:
            graph[row[-1]].sort(key=lambda x: len(graph[x]))
            nxt = None
            for v in graph[row[-1]]:
                if v not in seen and len(graph[v]) in (corner_deg, corner_deg + 1):
                    nxt = v
                    break
            if nxt is None:
                break
            row.append(nxt)
            seen.add(nxt)

        cols = len(row)
        rows = n // cols
        ans = [[0] * cols for _ in range(rows)]
        ans[0] = row
        for i in range(1, rows):
            for j in range(cols):
                for v in graph[ans[i - 1][j]]:
                    if v not in seen:
                        ans[i][j] = v
                        seen.add(v)
                        break
        return ans
# @lc code=end
