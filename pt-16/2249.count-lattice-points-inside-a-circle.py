#
# @lc app=leetcode id=2249 lang=python3
#
# [2249] Count Lattice Points Inside a Circle
#
# https://leetcode.com/problems/count-lattice-points-inside-a-circle/description/
#
# algorithms
# Medium (56.98%)
# Likes:    259
# Dislikes: 223
# Total Accepted:    33.6K
# Total Submissions: 59.1K
# Testcase Example:  "[[2,2,1]]"
#
# Given a 2D integer array circles where circles[i] = [x_i, y_i, r_i] represents
# the center (x_i, y_i) and radius r_i of the i^th circle drawn on a grid,
# return the number of lattice points that are present inside at least one
# circle.
#
# Note:
#
#
# A lattice point is a point with integer coordinates.
#
#
# Points that lie on the circumference of a circle are also considered to be
# inside it.
#
#
#
# Example 1:
#
# Input: circles = [[2,2,1]]
# Output: 5
# Explanation:
# The figure above shows the given circle.
# The lattice points present inside the circle are (1, 2), (2, 1), (2, 2), (2,
# 3), and (3, 2) and are shown in green.
# Other points such as (1, 1) and (1, 3), which are shown in red, are not
# considered inside the circle.
# Hence, the number of lattice points present inside at least one circle is 5.
#
# Example 2:
#
# Input: circles = [[2,2,2],[3,4,1]]
# Output: 16
# Explanation:
# The figure above shows the given circles.
# There are exactly 16 lattice points which are present inside at least one
# circle.
# Some of them are (0, 2), (2, 0), (2, 4), (3, 2), and (4, 4).
#
#
#
# Constraints:
#
#
# 1 <= circles.length <= 200
#
#
# circles[i].length == 3
#
#
# 1 <= x_i, y_i <= 100
#
#
# 1 <= r_i <= min(x_i, y_i)
#

# @lc code=start
from typing import List


class Solution:
    def countLatticePoints(self, circles: List[List[int]]) -> int:
        """
        Interview explanation:
        Count distinct integer lattice points lying inside or on at least one
        circle (x,y,r).

        Algorithm:
        - Enumerate candidate points in bounding box of each circle; use a set;
          check (dx^2+dy^2) <= r^2.

        Complexity: O(sum r^2) time, O(answer) space.
        """
        pts = set()
        for x, y, r in circles:
            for i in range(x - r, x + r + 1):
                for j in range(y - r, y + r + 1):
                    if (i - x) * (i - x) + (j - y) * (j - y) <= r * r:
                        pts.add((i, j))
        return len(pts)
# @lc code=end
