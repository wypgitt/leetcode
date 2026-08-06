#
# @lc app=leetcode id=3710 lang=python3
#
# [3710] Maximum Partition Factor
#
# https://leetcode.com/problems/maximum-partition-factor/description/
#
# algorithms
# Hard (32.29%)
# Likes:    83
# Dislikes: 7
# Total Accepted:    7.3K
# Total Submissions: 22.7K
# Testcase Example:  "[[0,0],[0,2],[2,0],[2,2]]"
#
#
# You are given a 2D integer array points, where points[i] = [x_i, y_i]
# represents the coordinates of the i^th point on the Cartesian plane.
#
# The Manhattan distance between two points points[i] = [x_i, y_i] and
# points[j] = [x_j, y_j] is |x_i - x_j| + |y_i - y_j|.
#
# Split the n points into exactly two non-empty groups. The partition
# factor of a split is the minimum Manhattan distance among all unordered
# pairs of points that lie in the same group.
#
# Return the maximum possible partition factor over all valid splits.
#
# Note: A group of size 1 contributes no intra-group pairs. When n = 2
# (both groups size 1), there are no intra-group pairs, so define the
# partition factor as 0.
#
# Example 1:
#
# Input: points = [[0,0],[0,2],[2,0],[2,2]]
#
# Output: 4
#
# Explanation:
#
# We split the points into two groups: {[0, 0], [2, 2]} and {[0, 2], [2,
# 0]}.
#
# In the first group, the only pair has Manhattan distance |0 - 2| + |0 -
# 2| = 4.
#
# In the second group, the only pair also has Manhattan distance |0 - 2| +
# |2 - 0| = 4.
#
# The partition factor of this split is min(4, 4) = 4, which is maximal.
#
# Example 2:
#
# Input: points = [[0,0],[0,1],[10,0]]
#
# Output: 11
#
# Explanation:​​​​​​​
#
# We split the points into two groups: {[0, 1], [10, 0]} and {[0, 0]}.
#
# In the first group, the only pair has Manhattan distance |0 - 10| + |1 -
# 0| = 11.
#
# The second group is a singleton, so it contributes no pairs.
#
# The partition factor of this split is 11, which is maximal.
#
# Constraints:
#
# 2 <= points.length <= 500
#
# points[i] = [x_i, y_i]
#
# -10^8 <= x_i, y_i <= 10^8
#

# @lc code=start

from typing import List


class Solution:
    def maxPartitionFactor(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Maximize D such that points can be 2-colored so every pair closer than D
        is split across groups (intra-group min distance >= D). n == 2 => 0.

        Algorithm:
        - Binary search D. For mid, build conflict graph (edge iff dist < mid).
        - Feasible iff the graph is bipartite (BFS/DFS 2-coloring).
        - Answer is the largest feasible D.

        Complexity: O(n^2 log M) time, O(n^2) space (M = max Manhattan distance).
        """
        n = len(points)
        if n == 2:
            return 0

        dist = [[0] * n for _ in range(n)]
        maxd = 0
        for i in range(n):
            x1, y1 = points[i]
            for j in range(i + 1, n):
                d = abs(x1 - points[j][0]) + abs(y1 - points[j][1])
                dist[i][j] = dist[j][i] = d
                if d > maxd:
                    maxd = d

        def ok(D: int) -> bool:
            color = [-1] * n
            for start in range(n):
                if color[start] != -1:
                    continue
                color[start] = 0
                stack = [start]
                while stack:
                    u = stack.pop()
                    for v in range(n):
                        if u == v or dist[u][v] >= D:
                            continue
                        if color[v] == -1:
                            color[v] = color[u] ^ 1
                            stack.append(v)
                        elif color[v] == color[u]:
                            return False
            return True

        lo, hi = 0, maxd
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if ok(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
