#
# @lc app=leetcode id=3625 lang=python3
#
# [3625] Count Number of Trapezoids II
#
#
# --- Interview Notes ---------------------------------------------------------
#
# Problem restatement
# We are given n distinct points on the plane. Count how many ways to choose
# four points that form a convex quadrilateral with at least one pair of parallel
# sides.
#
# A trapezoid here is inclusive: a parallelogram is also a trapezoid because it
# has at least one pair of parallel sides.
#
#
# Core idea
# Instead of checking every 4-point set, count possible pairs of parallel sides.
#
# A non-parallelogram trapezoid has exactly one pair of parallel opposite sides,
# so it is counted once by this method.
#
# A parallelogram has two pairs of parallel opposite sides, so it is counted
# twice. We subtract the number of non-degenerate parallelograms once at the end.
#
# Therefore:
#   answer = (# choices of two parallel non-collinear side segments)
#            - (# non-degenerate parallelograms)
#
#
# Counting pairs of parallel side segments
# Any two distinct parallel lines can serve as the supporting lines of the two
# parallel sides. If one line contains a points and the other contains b points,
# then:
#   C(a, 2) choices for a segment on the first line
#   C(b, 2) choices for a segment on the second line
#
# Each pair of such segments forms a convex trapezoid with those two segments as
# opposite sides.
#
# So for each slope:
#   1. Group all point-pairs by their exact line.
#   2. For each line, count how many segments lie on it.
#   3. Sum products of segment counts over pairs of distinct parallel lines.
#
# This avoids counting degenerate four-collinear choices, because both sides
# must come from two different parallel lines.
#
#
# Representing slopes and lines exactly
# Coordinates are integers, so we avoid floating-point slopes.
#
# For two points (x1, y1), (x2, y2):
#   dx = x2 - x1
#   dy = y2 - y1
#
# Normalize the direction:
#   divide by gcd(abs(dx), abs(dy))
#   force a canonical sign
#
# Example:
#   (2, 4) and (-1, -2) both normalize to (1, 2).
#
# For a normalized direction (dx, dy), an exact line can be represented with a
# perpendicular normal:
#   dy * x - dx * y = c
#
# Since dx and dy are normalized, c uniquely identifies a line among lines with
# that slope.
#
#
# Counting parallelograms
# A quadrilateral is a parallelogram iff its diagonals have the same midpoint.
#
# For every point pair, treat it as a possible diagonal and group by:
#   midpoint key = (x1 + x2, y1 + y2)
#
# We use doubled midpoint coordinates to avoid fractions.
#
# If a midpoint group has t diagonal candidates, then C(t, 2) pairs of diagonals
# share the same midpoint.
#
# However, two diagonal candidates with the same midpoint and the same slope are
# collinear, producing four collinear points instead of a convex parallelogram.
# These are degenerate and must not be subtracted as parallelograms.
#
# So for each midpoint group:
#   nondegenerate parallelograms =
#       C(total_diagonals, 2) - sum over slopes C(diagonals_with_that_slope, 2)
#
#
# Why subtract parallelograms?
# Our first count chooses one pair of parallel opposite sides.
#
# A normal trapezoid has only one such pair, so it appears once.
# A parallelogram has two such pairs, so it appears twice.
#
# Since the final answer should count each 4-point set once, subtract each
# non-degenerate parallelogram once.
#
#
# Data structures
#
# 1. lines_by_slope: defaultdict(Counter)
#    Maps:
#      slope -> {line_constant -> number_of_segments_on_that_line}
#
#    This supports the first count:
#      for each slope, combine segment counts from different lines.
#
# 2. midpoint_groups: dictionary
#    Maps:
#      midpoint -> [total_diagonal_count, Counter({diagonal_slope: count})]
#
#    This supports parallelogram counting while excluding degenerate collinear
#    diagonal pairs.
#
# Both structures are built from all O(n^2) point pairs.
#
#
# Walkthrough of the code
# 1. Iterate over every point pair.
# 2. Compute its normalized direction.
# 3. Add the segment to lines_by_slope[slope][line_constant].
# 4. Add the segment as a diagonal candidate in midpoint_groups[midpoint].
# 5. For every slope group, use a running sum to compute pair products across
#    distinct lines:
#      total += previous_segment_sum * current_line_segment_count
# 6. For every midpoint group, count non-degenerate parallelograms:
#      C(total, 2) - sum C(same_slope_count, 2)
# 7. Return:
#      parallel_side_pairs - parallelograms
#
#
# Correctness proof
#
# Lemma 1: Every pair of segments lying on two distinct parallel lines forms a
# convex quadrilateral with one pair of parallel opposite sides.
# Proof:
# The two segments are non-collinear because their supporting lines are distinct.
# Connecting their endpoints in order forms a convex quadrilateral whose chosen
# segments are opposite sides. Those sides are parallel by construction.
#
# Lemma 2: Every trapezoid is counted by the parallel-side-pair count once if it
# is not a parallelogram, and twice if it is a parallelogram.
# Proof:
# A non-parallelogram trapezoid has exactly one pair of parallel opposite sides,
# so only that side pair contributes. A parallelogram has two pairs of parallel
# opposite sides, so either pair can be chosen, producing two counts.
#
# Lemma 3: The line grouping counts exactly all pairs of parallel non-collinear
# side segments.
# Proof:
# A slope group contains exactly segments with that slope. Splitting by line
# constant separates collinear segments. Pairing segment counts from different
# lines chooses two parallel, non-collinear segments. Every such segment pair
# belongs to exactly one slope group and one pair of line groups.
#
# Lemma 4: The midpoint formula counts exactly non-degenerate parallelograms.
# Proof:
# A quadrilateral is a parallelogram iff its diagonals share a midpoint, so any
# two point-pairs in the same midpoint group define a parallelogram candidate.
# If the two diagonals have the same slope, all four points are collinear, so the
# candidate is degenerate. If their slopes differ, the four points form a
# non-degenerate parallelogram. Therefore subtracting same-slope diagonal pairs
# leaves exactly the non-degenerate parallelograms.
#
# Theorem: The algorithm returns the number of unique trapezoids.
# Proof:
# By Lemma 3, the first count equals the number of ways to choose parallel
# opposite side segments. By Lemma 2, this counts each non-parallelogram
# trapezoid once and each parallelogram twice. By Lemma 4, the second count is
# exactly the number of parallelograms. Subtracting it makes every trapezoid,
# including parallelograms, counted exactly once.
#
#
# Complexity analysis
#
# Let n = len(points).
#
# Time:
#   - There are O(n^2) point pairs.
#   - Each pair does O(log C) gcd work, where C is the coordinate range.
#   - Combining groups is O(number of generated pairs/lines), also O(n^2).
#   Overall time complexity: O(n^2 log C), effectively O(n^2) for these bounds.
#
# Space:
#   - We store information for O(n^2) segments in the worst case.
#   Overall space complexity: O(n^2).
#
#
# Tests to discuss in an interview
#
# 1. Example 1:
#      points = [[-3,2],[3,0],[2,3],[3,2],[2,-3]] -> 2
#
# 2. Example 2:
#      points = [[0,0],[1,0],[0,1],[2,1]] -> 1
#
# 3. All four points collinear:
#      [[0,0],[1,0],[2,0],[3,0]] -> 0
#      This verifies that same-line segment pairs are not counted.
#
# 4. A square:
#      [[0,0],[1,0],[1,1],[0,1]] -> 1
#      The side-pair count sees two parallel directions, then subtracts one
#      parallelogram duplicate.
#
# 5. Random brute force:
#      For small n, enumerate every 4-point subset, compute its convex hull, and
#      check whether opposite sides are parallel. Compare with this O(n^2)
#      solution.
#
#
# Edge cases
#
# - Vertical lines: normalized direction handles dx = 0 exactly.
# - Horizontal lines: normalized direction handles dy = 0 exactly.
# - Multiple points on the same line: line grouping counts all segment choices
#   but only pairs them with segments from different parallel lines.
# - Degenerate midpoint pairs: same-midpoint, same-slope diagonals are excluded
#   from the parallelogram subtraction.
#
#
# Possible improvements
#
# - Since n <= 500, O(n^2) segment enumeration is appropriate.
# - A brute-force O(n^4) quadrilateral check is too slow: C(500, 4) is over
#   2.5 billion subsets.
# - Floating-point slope comparisons should be avoided; normalized integer
#   directions are exact and robust.
#
# -------------------------------------------------------------------------------

# @lc code=start
from collections import defaultdict
from math import gcd
from typing import Dict, List, Tuple


class Solution:
    def countTrapezoids(self, points: List[List[int]]) -> int:
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
        common = gcd(abs(dx), abs(dy))
        dx //= common
        dy //= common
        if dx < 0 or (dx == 0 and dy < 0):
            dx = -dx
            dy = -dy
        return dx, dy


# @lc code=end
