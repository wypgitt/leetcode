#
# @lc app=leetcode id=3623 lang=python3
#
# [3623] Count Number of Trapezoids I
#
# https://leetcode.com/problems/count-number-of-trapezoids-i/description/
#
# algorithms
# Medium (48.08%)
# Likes:    401
# Dislikes: 51
# Total Accepted:    119.4K
# Total Submissions: 248.3K
# Testcase Example:  "[[1,0],[2,0],[3,0],[2,2],[3,2]]"
#
#
# You are given a 2D integer array points, where points[i] = [x_i, y_i]
# represents the coordinates of the i^th point on the Cartesian plane.
#
# A horizontal trapezoid is a convex quadrilateral with at least one pair
# of horizontal sides (i.e. parallel to the x-axis). Two lines are
# parallel if and only if they have the same slope.
#
# Return the  number of unique horizontal trapezoids that can be formed by
# choosing any four distinct points from points.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: points = [[1,0],[2,0],[3,0],[2,2],[3,2]]
#
# Output: 3
#
# Explanation:
#
# There are three distinct ways to pick four points that form a horizontal
# trapezoid:
#
# Using points [1,0], [2,0], [3,2], and [2,2].
#
# Using points [2,0], [3,0], [3,2], and [2,2].
#
# Using points [1,0], [3,0], [3,2], and [2,2].
#
# Example 2:
#
# Input: points = [[0,0],[1,0],[0,1],[2,1]]
#
# Output: 1
#
# Explanation:
#
# There is only one horizontal trapezoid that can be formed.
#
# Constraints:
#
# 4 <= points.length <= 10^5
#
# –10^8 <= x_i, y_i <= 10^8
#
# All points are pairwise distinct.
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def countTrapezoids(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Horizontal trapezoids need two distinct y-levels, each contributing a
        horizontal side (any 2 points on that y). Count pairs of horizontal
        edges from different y's.

        Algorithm:
        - Count points per y-coordinate.
        - For each y with c points, edges = C(c, 2).
        - Accumulate sum over pairs of y's of edges_i * edges_j via running
          total: ans += total * curr; total += curr. Mod 1e9+7.

        Complexity: O(n) time, O(n) space.
        """
        MOD = 10**9 + 7
        cnt = defaultdict(int)
        for _, y in points:
            cnt[y] += 1
        ans = total = 0
        for c in cnt.values():
            curr = (c * (c - 1) // 2) % MOD
            ans = (ans + total * curr) % MOD
            total = (total + curr) % MOD
        return ans
# @lc code=end

