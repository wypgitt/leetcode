#
# @lc app=leetcode id=1453 lang=python3
#
# [1453] Maximum Number of Darts Inside of a Circular Dartboard
#
# https://leetcode.com/problems/maximum-number-of-darts-inside-of-a-circular-dartboard/description/
#
# algorithms
# Hard (41.29%)
# Likes:    160
# Dislikes: 277
# Total Accepted:    9.2K
# Total Submissions: 22.2K
# Testcase Example:  "[[-2,0],[2,0],[0,2],[0,-2]]"
#
# Alice is throwing n darts on a very large wall. You are given an array darts
# where darts[i] = [x_i, y_i] is the position of the i^th dart that Alice threw
# on the wall.
#
# Bob knows the positions of the n darts on the wall. He wants to place a
# dartboard of radius r on the wall so that the maximum number of darts that
# Alice throws lie on the dartboard.
#
# Given the integer r, return the maximum number of darts that can lie on the
# dartboard.
#
# Example 1:
#
# Input: darts = [[-2,0],[2,0],[0,2],[0,-2]], r = 2
# Output: 4
# Explanation: Circle dartboard with center in (0,0) and radius = 2 contain all
# points.
#
# Example 2:
#
# Input: darts = [[-3,0],[3,0],[2,6],[5,4],[0,9],[7,8]], r = 5
# Output: 5
# Explanation: Circle dartboard with center in (0,4) and radius = 5 contain all
# points except the point (7,8).
#
# Constraints:
#
# 1 <= darts.length <= 100
#
# darts[i].length == 2
#
# -10^4 <= x_i, y_i <= 10^4
#
# All the darts are unique
#
# 1 <= r <= 5000
#

# @lc code=start
from typing import List
import math


class Solution:
    def numPoints(self, darts: List[List[int]], r: int) -> int:
        """
        Interview explanation:
        Place a disk of radius r covering the maximum number of points. Optimal
        circles can be chosen so that at least two points lie on the boundary
        (or one point as center for r-cover). For each pair, compute up to two
        circle centers of radius r through both points; count points within r.

        Algorithm:
        - ans = 1; for each pair i,j with dist<=2r, compute center(s); count
          points with dist(center,p)<=r (+eps); also count singles.

        Complexity: O(n^3) time, O(1) extra space.
        """
        n = len(darts)
        if n == 0:
            return 0
        ans = 1
        eps = 1e-8
        r2 = r * r

        def dist2(a, b):
            return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

        def centers(p, q):
            # Circles of radius r with p,q on boundary
            d2 = dist2(p, q)
            if d2 > 4 * r2 + eps:
                return []
            if d2 < eps:
                return []
            mx = (p[0] + q[0]) / 2.0
            my = (p[1] + q[1]) / 2.0
            d = math.sqrt(d2)
            h = math.sqrt(max(0.0, r2 - d2 / 4.0))
            dx = (q[0] - p[0]) / d
            dy = (q[1] - p[1]) / d
            return [
                (mx - h * dy, my + h * dx),
                (mx + h * dy, my - h * dx),
            ]

        def count(cx, cy):
            c = 0
            for x, y in darts:
                if (x - cx) ** 2 + (y - cy) ** 2 <= r2 + eps:
                    c += 1
            return c

        for i in range(n):
            for j in range(i + 1, n):
                for cx, cy in centers(darts[i], darts[j]):
                    ans = max(ans, count(cx, cy))
        return ans
# @lc code=end
