#
# @lc app=leetcode id=149 lang=python3
#
# [149] Max Points on a Line
#
# https://leetcode.com/problems/max-points-on-a-line/description/
#
# algorithms
# Hard (31.19%)
# Likes:    4570
# Dislikes: 600
# Total Accepted:    546K
# Total Submissions: 1.7M
# Testcase Example:  "[[1,1],[2,2],[3,3]]"
#
# Given an array of points where points[i] = [x_i, y_i] represents a point on
# the X-Y plane, return the maximum number of points that lie on the same
# straight line.
#
# Example 1:
#
# Input: points = [[1,1],[2,2],[3,3]]
# Output: 3
#
# Example 2:
#
# Input: points = [[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]]
# Output: 4
#
# Constraints:
#
# 1 <= points.length <= 300
#
# points[i].length == 2
#
# -10^4 <= x_i, y_i <= 10^4
#
# All the points are unique.
#

# @lc code=start
from collections import defaultdict
from math import gcd
from typing import List


class Solution:
    def maxPoints(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        For each pivot point, group other points by reduced slope (dx, dy) using
        gcd so collinear points share one key. The best group size plus the pivot
        is the answer for that pivot.

        Algorithm:
        - Answer is at least 1 if points exist.
        - For each i, map reduced (dx, dy) -> count among j > i (or all j != i).
        - Normalize signs so opposite directions of the same line collide.
        - Track max over slopes; update global max with count + 1.

        Complexity: O(n^2 * log A) time from gcd, O(n) space per pivot.
        """
        n = len(points)
        if n <= 2:
            return n

        ans = 1
        for i in range(n):
            slopes = defaultdict(int)
            x1, y1 = points[i]
            local = 0
            for j in range(n):
                if i == j:
                    continue
                x2, y2 = points[j]
                dx, dy = x2 - x1, y2 - y1
                g = gcd(dx, dy)
                dx //= g
                dy //= g
                if dx < 0 or (dx == 0 and dy < 0):
                    dx, dy = -dx, -dy
                slopes[(dx, dy)] += 1
                local = max(local, slopes[(dx, dy)])
            ans = max(ans, local + 1)
        return ans
# @lc code=end
