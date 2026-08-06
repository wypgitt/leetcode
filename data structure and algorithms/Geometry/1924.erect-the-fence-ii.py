#
# @lc app=leetcode id=1924 lang=python3
#
# [1924] Erect the Fence II
#
# https://leetcode.com/problems/erect-the-fence-ii/description/
#
# algorithms
# Hard (51.60%)
# Likes:    15
# Dislikes: 44
# Total Accepted:    1K
# Total Submissions: 2K
# Testcase Example:  "[[1,1],[2,2],[2,0],[2,4],[3,3],[4,2]]"
#
#
# You are given a 2D integer array trees where trees[i] = [x_i, y_i]
# represents the location of the i^th tree in the garden.
#
# You are asked to fence the entire garden using the minimum length of
# rope possible. The garden is well-fenced only if all the trees are
# enclosed and the rope used forms a perfect circle. A tree is considered
# enclosed if it is inside or on the border of the circle.
#
# More formally, you must form a circle using the rope with a center (x,
# y) and radius r where all trees lie inside or on the circle and r is
# minimum.
#
# Return the center and radius of the circle as a length 3 array [x, y,
# r]. Answers within 10^-5 of the actual answer will be accepted.
#
# Example 1:
#
# Input: trees = [[1,1],[2,2],[2,0],[2,4],[3,3],[4,2]]
# Output: [2.00000,2.00000,2.00000]
# Explanation: The fence will have center = (2, 2) and radius = 2
#
# Example 2:
#
# Input: trees = [[1,2],[2,2],[4,2]]
# Output: [2.50000,2.00000,1.50000]
# Explanation: The fence will have center = (2.5, 2) and radius = 1.5
#
# Constraints:
#
# 1 <= trees.length <= 3000
#
# trees[i].length == 2
#
# 0 <= x_i, y_i <= 3000
#
# @lc code=start
from typing import List
import math
import random


class Solution:
    def outerTrees(self, trees: List[List[int]]) -> List[float]:
        """
        Interview explanation:
        Premium. Smallest circle covering all points (minimum enclosing circle).
        Welzl's randomized incremental algorithm: shuffle; grow circle when a
        point is outside, recursively with boundary constraints (0/1/2/3 points).

        Algorithm:
        - circle from 0-3 boundary points; for each point outside, recompute
          with that point forced on boundary.

        Complexity: Expected O(n) time, O(n) space.
        """
        pts = [(float(x), float(y)) for x, y in trees]
        random.shuffle(pts)

        def dist2(a, b):
            return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

        def circle2(a, b):
            cx = (a[0] + b[0]) / 2
            cy = (a[1] + b[1]) / 2
            r = math.sqrt(dist2(a, b)) / 2
            return cx, cy, r

        def circle3(a, b, c):
            ax, ay = a
            bx, by = b
            cx, cy = c
            d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            if abs(d) < 1e-12:
                # collinear: diameter = farthest pair
                pairs = [(a, b), (a, c), (b, c)]
                u, v = max(pairs, key=lambda p: dist2(p[0], p[1]))
                return circle2(u, v)
            ux = (
                (ax * ax + ay * ay) * (by - cy)
                + (bx * bx + by * by) * (cy - ay)
                + (cx * cx + cy * cy) * (ay - by)
            ) / d
            uy = (
                (ax * ax + ay * ay) * (cx - bx)
                + (bx * bx + by * by) * (ax - cx)
                + (cx * cx + cy * cy) * (bx - ax)
            ) / d
            r = math.sqrt((ux - ax) ** 2 + (uy - ay) ** 2)
            return ux, uy, r

        def inside(cir, p):
            if cir is None:
                return False
            cx, cy, r = cir
            return (p[0] - cx) ** 2 + (p[1] - cy) ** 2 <= r * r + 1e-8

        def welzl(i, R):
            if i == 0 or len(R) == 3:
                if len(R) == 0:
                    return (0.0, 0.0, 0.0)
                if len(R) == 1:
                    return (R[0][0], R[0][1], 0.0)
                if len(R) == 2:
                    return circle2(R[0], R[1])
                return circle3(R[0], R[1], R[2])
            cir = welzl(i - 1, R)
            if inside(cir, pts[i - 1]):
                return cir
            return welzl(i - 1, R + [pts[i - 1]])

        cx, cy, r = welzl(len(pts), [])
        return [cx, cy, r]
# @lc code=end
