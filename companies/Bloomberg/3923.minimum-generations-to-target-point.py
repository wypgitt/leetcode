#
# @lc app=leetcode id=3923 lang=python3
#
# [3923] Minimum Generations to Target Point
#
# https://leetcode.com/problems/minimum-generations-to-target-point/description/
#
# algorithms
# Medium (44.26%)
# Likes:    28
# Dislikes: 11
# Total Accepted:    11.9K
# Total Submissions: 27K
# Testcase Example:  "[[0,0,0],[6,6,6]]\n[3,3,3]"
#
#
# You are given a 2D integer array points where points[i] = [x_i, y_i,
# z_i] represents a point in 3D space, and an integer array target
# representing a target point.
#
# Define generation 0 as the initial list of points. For each integer k >=
# 1, form generation k as follows:
#
# Consider every pair of two distinct points a = [x_1, y_1, z_1] and b =
# [x_2, y_2, z_2] taken from all points produced in generations 0 through
# k - 1.
#
# For each such pair, compute c = [floor((x_1 + x_2) / 2), floor((y_1 +
# y_2) / 2), floor((z_1 + z_2) / 2)] and collect every such c into a
# generation k.
#
# All points in the generation k are produced simultaneously from points
# in generations 0 through​​​​​​​ k - 1.
#
# After generation k is formed, the points in the generation k are
# considered available for forming later generations.
#
# Return the smallest integer k such that the target appears in one of the
# generations 0 through k. If the target is already in the initial points,
# return 0. If it is impossible to obtain the target, return -1.
#
# Notes:
#
# floor denotes rounding down to the nearest integer.
#
# "Two distinct points" means the two chosen points must have different
# (x, y, z) coordinates. A point cannot be paired with itself, and pairing
# two points with identical coordinates is not possible.
#
# Example 1:
#
# Input: points = [[0,0,0],[6,6,6]], target = [3,3,3]
#
# Output: 1
#
# Explanation:
#
# Generation 0: The initial points = [[0, 0, 0], [6, 6, 6]].
#
# The target = [3, 3, 3] does not exist in generation 0.
#
# Generation 1: For each pair of points in generation 0, we create new
# points.
#
# Using [0, 0, 0] and [6, 6, 6], we generate [3, 3, 3].
#
# After generation 1, points = [[0, 0, 0], [6, 6, 6], [3, 3, 3]].
#
# The target = [3, 3, 3] is found in generation 1, so the smallest k is 1.
#
# Example 2:
#
# Input: points = [[0,0,0],[5,5,5]], target = [1,1,1]
#
# Output: 2
#
# Explanation:
#
# Generation 0: The initial points = [[0, 0, 0], [5, 5, 5]].
#
# The target = [1, 1, 1] does not exist in generation 0.
#
# Generation 1: For each pair of points in generation 0, we create new
# points.
#
# Using [0, 0, 0] and [5, 5, 5], we generate [2, 2, 2].
#
# After generation 1, points = [[0, 0, 0], [5, 5, 5], [2, 2, 2]].
#
# Generation 2: For each pair of points available after generation 1, we
# create new points.
#
# Using [0, 0, 0] and [5, 5, 5], we generate [2, 2, 2].
#
# Using [0, 0, 0] and [2, 2, 2], we generate [1, 1, 1].
#
# Using [5, 5, 5] and [2, 2, 2], we generate [3, 3, 3].
#
# After generation 2, points = [[0, 0, 0], [5, 5, 5], [2, 2, 2], [1, 1,
# 1], [3, 3, 3]].
#
# The target = [1, 1, 1] is found in generation 2, so the smallest k is 2.
#
# Example 3:
#
# Input: points = [[0,0,0],[2,2,2],[3,3,3]], target = [2,2,2]
#
# Output: 0
#
# Explanation:
#
# Generation 0: The initial points = [[0, 0, 0], [2, 2, 2], [3, 3, 3]].
#
# The target = [2, 2, 2] already exists in generation 0, so the smallest k
# is 0.
#
# Example 4:
#
# Input: points = [[1,2,3]], target = [5,5,5]
#
# Output: -1
#
# Explanation:
#
# Only one initial point is available, so no new points can be generated.
#
# Therefore, the target cannot be obtained, and the answer is -1.
#
# Constraints:
#
# 1 <= points.length <= 20
#
# points[i] = [x_i, y_i, z_i​​​​​​​]
#
# 0 <= x_i, y_i, z_i <= 6
#
# target.length == 3
#
# ​​​​​​​0 <= target[i] <= 6
#
# The initial set of points contains no duplicates.
#

# @lc code=start

from typing import List


class Solution:
    def minGenerations(self, points: List[List[int]], target: List[int]) -> int:
        """
        Interview explanation:
        Each generation takes floor-midpoints of every distinct pair among all
        points seen so far. Coordinates are tiny (0..6), so at most 7^3 points;
        simulate generations until the target appears or the set stabilizes.

        Algorithm:
        - Start from the unique initial points (generation 0).
        - Repeatedly form all floor-midpoints of pairs; assign each newly seen
          point the current generation index.
        - Stop when target is found or no new points appear.

        Complexity: O(P^3) time with P <= 343, O(P) space.
        """
        morvilexa = points
        t = (target[0], target[1], target[2])
        seen = {(p[0], p[1], p[2]) for p in morvilexa}
        if t in seen:
            return 0
        pts = list(seen)
        gen = 0
        while True:
            gen += 1
            new_pts = []
            n = len(pts)
            for i in range(n):
                x1, y1, z1 = pts[i]
                for j in range(i + 1, n):
                    x2, y2, z2 = pts[j]
                    c = ((x1 + x2) // 2, (y1 + y2) // 2, (z1 + z2) // 2)
                    if c not in seen:
                        seen.add(c)
                        new_pts.append(c)
                        if c == t:
                            return gen
            if not new_pts:
                return -1
            pts.extend(new_pts)
# @lc code=end
