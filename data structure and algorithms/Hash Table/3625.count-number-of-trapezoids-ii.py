#
# @lc app=leetcode id=3625 lang=python3
#
# [3625] Count Number of Trapezoids II
#
# https://leetcode.com/problems/count-number-of-trapezoids-ii/description/
#
# algorithms
# Hard (39.72%)
# Likes:    265
# Dislikes: 98
# Total Accepted:    58.4K
# Total Submissions: 146.9K
# Testcase Example:  "[[-3,2],[3,0],[2,3],[3,2],[2,-3]]"
#
#
# You are given a 2D integer array points where points[i] = [x_i, y_i]
# represents the coordinates of the i^th point on the Cartesian plane.
#
# Return the number of unique trapezoids that can be formed by choosing
# any four distinct points from points.
#
# A trapezoid is a convex quadrilateral with at least one pair of parallel
# sides. Two lines are parallel if and only if they have the same slope.
#
# Example 1:
#
# Input: points = [[-3,2],[3,0],[2,3],[3,2],[2,-3]]
#
# Output: 2
#
# Explanation:
#
# There are two distinct ways to pick four points that form a trapezoid:
#
# The points [-3,2], [2,3], [3,2], [2,-3] form one trapezoid.
#
# The points [2,3], [3,2], [3,0], [2,-3] form another trapezoid.
#
# Example 2:
#
# Input: points = [[0,0],[1,0],[0,1],[2,1]]
#
# Output: 1
#
# Explanation:
#
# There is only one trapezoid which can be formed.
#
# Constraints:
#
# 4 <= points.length <= 500
#
# –1000 <= x_i, y_i <= 1000
#
# All points are pairwise distinct.
#

# @lc code=start

from collections import defaultdict
from math import gcd
from typing import Dict, List, Tuple


class Solution:
    def countTrapezoids(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Count convex trapezoids (>=1 pair of parallel sides) among n<=500
        points. Count unordered pairs of segments that share a slope but lie
        on different lines; each such pair is a trapezoid candidate. A
        parallelogram is counted twice (two pairs of parallel sides), so
        subtract the parallelogram count once.

        Algorithm:
        - For every pair of points, normalize direction (dx,dy) and line id;
          tally segments per (slope -> line).
        - Also group segments by midpoint and direction to detect diagonal
          pairs that form parallelograms.
        - parallel_side_pairs = sum over slopes of pairs of segments on
          distinct lines; parallelograms from midpoint double-counting fix;
          answer = parallel_side_pairs - parallelograms.

        Complexity: O(n^2) time, O(n^2) space.
        """
        lines_by_slope: Dict[Tuple[int, int], Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        midpoint_groups = defaultdict(lambda: [0, defaultdict(int)])

        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            for j in range(i + 1, n):
                x2, y2 = points[j]
                dx, dy = self._direction(x2 - x1, y2 - y1)

                line_constant = dy * x1 - dx * y1
                lines_by_slope[(dx, dy)][line_constant] += 1

                midpoint = (x1 + x2, y1 + y2)
                midpoint_groups[midpoint][0] += 1
                midpoint_groups[midpoint][1][(dx, dy)] += 1

        parallel_side_pairs = 0
        for line_counts in lines_by_slope.values():
            previous_segments = 0
            for segment_count in line_counts.values():
                parallel_side_pairs += previous_segments * segment_count
                previous_segments += segment_count

        parallelograms = 0
        for total_diagonals, slope_counts in midpoint_groups.values():
            current = total_diagonals * (total_diagonals - 1) // 2
            for same_slope in slope_counts.values():
                current -= same_slope * (same_slope - 1) // 2
            parallelograms += current

        return parallel_side_pairs - parallelograms

    def _direction(self, dx: int, dy: int) -> Tuple[int, int]:
        """
        Interview explanation:
        Canonical unit direction for a segment so opposite orientations match.

        Algorithm:
        - Divide by gcd; flip sign so dx>0, or dx==0 and dy>0.

        Complexity: O(log max(|dx|,|dy|)) time, O(1) space.
        """
        common = gcd(abs(dx), abs(dy))
        dx //= common
        dy //= common
        if dx < 0 or (dx == 0 and dy < 0):
            dx = -dx
            dy = -dy
        return dx, dy
# @lc code=end
