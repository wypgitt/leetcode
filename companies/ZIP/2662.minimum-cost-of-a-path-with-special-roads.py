#
# @lc app=leetcode id=2662 lang=python3
#
# [2662] Minimum Cost of a Path With Special Roads
#
# https://leetcode.com/problems/minimum-cost-of-a-path-with-special-roads/description/
#
# algorithms
# Medium (43.77%)
# Likes:    719
# Dislikes: 93
# Total Accepted:    21K
# Total Submissions: 48.1K
# Testcase Example:  "[1,1]\n[4,5]\n[[1,2,3,3,2],[3,4,4,5,1]]"
#
# You are given an array start where start = [startX, startY] represents your
# initial position (startX, startY) in a 2D space. You are also given the array
# target where target = [targetX, targetY] represents your target position
# (targetX, targetY).
#
# The cost of going from a position (x1, y1) to any other position in the space
# (x2, y2) is |x2 - x1| + |y2 - y1|.
#
# There are also some special roads. You are given a 2D array specialRoads where
# specialRoads[i] = [x1_i, y1_i, x2_i, y2_i, cost_i] indicates that the i^th
# special road goes in one direction from (x1_i, y1_i) to (x2_i, y2_i) with a
# cost equal to cost_i. You can use each special road any number of times.
#
# Return the minimum cost required to go from (startX, startY) to (targetX,
# targetY).
#
#
#
# Example 1:
#
# Input: start = [1,1], target = [4,5], specialRoads = [[1,2,3,3,2],[3,4,4,5,1]]
#
# Output: 5
#
# Explanation:
#
#
# (1,1) to (1,2) with a cost of |1 - 1| + |2 - 1| = 1.
#
#
# (1,2) to (3,3). Use specialRoads[0] with the cost 2.
#
#
# (3,3) to (3,4) with a cost of |3 - 3| + |4 - 3| = 1.
#
#
# (3,4) to (4,5). Use specialRoads[1] with the cost 1.
#
# So the total cost is 1 + 2 + 1 + 1 = 5.
#
# Example 2:
#
# Input: start = [3,2], target = [5,7], specialRoads =
# [[5,7,3,2,1],[3,2,3,4,4],[3,3,5,5,5],[3,4,5,6,6]]
#
# Output: 7
#
# Explanation:
#
# It is optimal not to use any special edges and go directly from the starting
# to the ending position with a cost |5 - 3| + |7 - 2| = 7.
#
# Note that the specialRoads[0] is directed from (5,7) to (3,2).
#
# Example 3:
#
# Input: start = [1,1], target = [10,4], specialRoads =
# [[4,2,1,1,3],[1,2,7,4,4],[10,3,6,1,2],[6,1,1,2,3]]
#
# Output: 8
#
# Explanation:
#
#
# (1,1) to (1,2) with a cost of |1 - 1| + |2 - 1| = 1.
#
#
# (1,2) to (7,4). Use specialRoads[1] with the cost 4.
#
#
# (7,4) to (10,4) with a cost of |10 - 7| + |4 - 4| = 3.
#
#
#
# Constraints:
#
#
# start.length == target.length == 2
#
#
# 1 <= startX <= targetX <= 10^5
#
#
# 1 <= startY <= targetY <= 10^5
#
#
# 1 <= specialRoads.length <= 200
#
#
# specialRoads[i].length == 5
#
#
# startX <= x1_i, x2_i <= targetX
#
#
# startY <= y1_i, y2_i <= targetY
#
#
# 1 <= cost_i <= 10^5
#

# @lc code=start

from typing import List
import heapq


class Solution:
    def minimumCost(self, start: List[int], target: List[int], specialRoads: List[List[int]]) -> int:
        """
        Interview explanation:
        Move on plane with cost |dx|+|dy|; may also take special roads (x1,y1)->(x2,y2) with given cost.
        Min cost from start to target.

        Algorithm:
        - Dijkstra over nodes {start, target} union special endpoints. Edges: manhattan between any
          pair of nodes, plus each special road as a directed shortcut.

        Complexity: O((S^2) log S) with S = #special roads.
        """
        sx, sy = start
        tx, ty = target
        nodes = [(sx, sy), (tx, ty)]
        for x1, y1, x2, y2, _ in specialRoads:
            nodes.append((x1, y1))
            nodes.append((x2, y2))
        # dedupe
        nodes = list(dict.fromkeys(nodes))
        idx = {p: i for i, p in enumerate(nodes)}
        N = len(nodes)
        g = [[] for _ in range(N)]
        for i in range(N):
            x1, y1 = nodes[i]
            for j in range(N):
                if i == j:
                    continue
                x2, y2 = nodes[j]
                g[i].append((j, abs(x1 - x2) + abs(y1 - y2)))
        for x1, y1, x2, y2, c in specialRoads:
            u, v = idx[(x1, y1)], idx[(x2, y2)]
            g[u].append((v, c))
        dist = [10**18] * N
        dist[idx[(sx, sy)]] = 0
        pq = [(0, idx[(sx, sy)])]
        while pq:
            d, u = heapq.heappop(pq)
            if d != dist[u]:
                continue
            for v, w in g[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        return dist[idx[(tx, ty)]]
# @lc code=end
