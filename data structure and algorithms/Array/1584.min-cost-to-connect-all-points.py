#
# @lc app=leetcode id=1584 lang=python3
#
# [1584] Min Cost to Connect All Points
#
# https://leetcode.com/problems/min-cost-to-connect-all-points/description/
#
# algorithms
# Medium (71.47%)
# Likes:    5730
# Dislikes: 149
# Total Accepted:    502K
# Total Submissions: 703K
# Testcase Example:  "[[0,0],[2,2],[3,10],[5,2],[7,0]]"
#
# You are given an array points representing integer coordinates of some points
# on a 2D-plane, where points[i] = [x_i, y_i].
#
# The cost of connecting two points [x_i, y_i] and [x_j, y_j] is the manhattan
# distance between them: |x_i - x_j| + |y_i - y_j|, where |val| denotes the
# absolute value of val.
#
# Return the minimum cost to make all points connected. All points are
# connected if there is exactly one simple path between any two points.
#
# Example 1:
#
# Input: points = [[0,0],[2,2],[3,10],[5,2],[7,0]]
# Output: 20
# Explanation:
#
# We can connect the points as shown above to get the minimum cost of 20.
# Notice that there is a unique path between every pair of points.
#
# Example 2:
#
# Input: points = [[3,12],[-2,5],[-4,1]]
# Output: 18
#
# Constraints:
#
# 1 <= points.length <= 1000
#
# -10^6 <= x_i, y_i <= 10^6
#
# All pairs (x_i, y_i) are distinct.
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def minCostConnectPoints(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        MST on complete graph with Manhattan distances. Prim with dense O(n^2)
        (or heap) is classic for n<=1000.

        Algorithm (Prim O(n^2)):
        - min_dist[i]=best edge into i; start 0; repeatedly add closest unused
          point updating distances.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(points)
        in_mst = [False] * n
        min_d = [10**18] * n
        min_d[0] = 0
        ans = 0
        for _ in range(n):
            u = -1
            best = 10**18
            for i in range(n):
                if not in_mst[i] and min_d[i] < best:
                    best = min_d[i]
                    u = i
            in_mst[u] = True
            ans += best
            x1, y1 = points[u]
            for v in range(n):
                if not in_mst[v]:
                    d = abs(x1 - points[v][0]) + abs(y1 - points[v][1])
                    if d < min_d[v]:
                        min_d[v] = d
        return ans

    def minCostConnectPoints_kruskal(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic alternate MST: Kruskal — all edges sorted, Union-Find add if
        connects different components.

        Algorithm (Kruskal):
        - Build all pairs Manhattan edges; sort by weight; UF until n-1 edges.

        Complexity: O(n^2 log n) time, O(n^2) space.
        """
        n = len(points)
        edges = []
        for i in range(n):
            for j in range(i + 1, n):
                d = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
                edges.append((d, i, j))
        edges.sort()
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        ans = used = 0
        for d, u, v in edges:
            ru, rv = find(u), find(v)
            if ru == rv:
                continue
            parent[rv] = ru
            ans += d
            used += 1
            if used == n - 1:
                break
        return ans

    def minCostConnectPoints_prim_heap(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate Prim with min-heap of candidate edges (like Dijkstra growth).

        Algorithm:
        - Heap (cost, node); pop unused; push Manhattan to all others.

        Complexity: O(n^2 log n) time, O(n^2) heap worst.
        """
        n = len(points)
        seen = [False] * n
        heap = [(0, 0)]
        ans = taken = 0
        while heap and taken < n:
            cost, u = heapq.heappop(heap)
            if seen[u]:
                continue
            seen[u] = True
            ans += cost
            taken += 1
            x1, y1 = points[u]
            for v in range(n):
                if not seen[v]:
                    d = abs(x1 - points[v][0]) + abs(y1 - points[v][1])
                    heapq.heappush(heap, (d, v))
        return ans
# @lc code=end

