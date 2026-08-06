#
# @lc app=leetcode id=1591 lang=python3
#
# [1591] Strange Printer II
#
# https://leetcode.com/problems/strange-printer-ii/description/
#
# algorithms
# Hard (60.94%)
# Likes:    703
# Dislikes: 24
# Total Accepted:    17.4K
# Total Submissions: 28.6K
# Testcase Example:  "[[1,1,1,1],[1,2,2,1],[1,2,2,1],[1,1,1,1]]"
#
# There is a strange printer with the following two special requirements:
#
# On each turn, the printer will print a solid rectangular pattern of a single
# color on the grid. This will cover up the existing colors in the rectangle.
#
# Once the printer has used a color for the above operation, the same color
# cannot be used again.
#
# You are given a m x n matrix targetGrid, where targetGrid[row][col] is the
# color in the position (row, col) of the grid.
#
# Return true if it is possible to print the matrix targetGrid, otherwise,
# return false.
#
# Example 1:
#
# Input: targetGrid = [[1,1,1,1],[1,2,2,1],[1,2,2,1],[1,1,1,1]]
# Output: true
#
# Example 2:
#
# Input: targetGrid = [[1,1,1,1],[1,1,3,3],[1,1,3,4],[5,5,1,4]]
# Output: true
#
# Example 3:
#
# Input: targetGrid = [[1,2,1],[2,1,2],[1,2,1]]
# Output: false
# Explanation: It is impossible to form targetGrid because it is not allowed to
# print the same color in different turns.
#
# Constraints:
#
# m == targetGrid.length
#
# n == targetGrid[i].length
#
# 1 <= m, n <= 60
#
# 1 <= targetGrid[row][col] <= 60
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def isPrintable(self, targetGrid: List[List[int]]) -> bool:
        """
        Interview explanation:
        Strange printer paints whole rectangles of one color. For each color,
        its bounding box must be that color or colors printed later. Build
        dependency: color A depends on B if B appears inside A's box (B printed
        after A). Topological order must exist (no cycle).

        Algorithm:
        - For each color find min/max r,c; scan box; edge color→other.
        - Kahn topo on colors; if not all processed → False.

        Complexity: O(C * mn + C^2) ~ O(mn * colors).
        """
        m, n = len(targetGrid), len(targetGrid[0])
        bounds = {}
        for i in range(m):
            for j in range(n):
                c = targetGrid[i][j]
                if c not in bounds:
                    bounds[c] = [i, i, j, j]
                else:
                    b = bounds[c]
                    b[0] = min(b[0], i)
                    b[1] = max(b[1], i)
                    b[2] = min(b[2], j)
                    b[3] = max(b[3], j)
        graph = defaultdict(set)
        indeg = {c: 0 for c in bounds}
        for c, (r1, r2, c1, c2) in bounds.items():
            seen = set()
            for i in range(r1, r2 + 1):
                for j in range(c1, c2 + 1):
                    other = targetGrid[i][j]
                    if other != c:
                        seen.add(other)
            for other in seen:
                # c must be printed before other (other overwrites inside c's box)
                if other not in graph[c]:
                    graph[c].add(other)
                    indeg[other] += 1
        q = deque([c for c, d in indeg.items() if d == 0])
        seen_cnt = 0
        while q:
            u = q.popleft()
            seen_cnt += 1
            for v in graph[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        return seen_cnt == len(bounds)
# @lc code=end

