#
# @lc app=leetcode id=3143 lang=python3
#
# [3143] Maximum Points Inside the Square
#
# https://leetcode.com/problems/maximum-points-inside-the-square/description/
#
# algorithms
# Medium (39.55%)
# Likes:    180
# Dislikes: 24
# Total Accepted:    22.2K
# Total Submissions: 56.2K
# Testcase Example:  "[[2,2],[-1,-2],[-4,4],[-3,1],[3,-3]]\n\"abdca\""
#
#
# You are given a 2D array points and a string s where, points[i]
# represents the coordinates of point i, and s[i] represents the tag of
# point i.
#
# A valid square is a square centered at the origin (0, 0), has edges
# parallel to the axes, and does not contain two points with the same tag.
#
# Return the maximum number of points contained in a valid square.
#
# Note:
#
# A point is considered to be inside the square if it lies on or within
# the square's boundaries.
#
# The side length of the square can be zero.
#
# Example 1:
#
# Input: points = [[2,2],[-1,-2],[-4,4],[-3,1],[3,-3]], s = "abdca"
#
# Output: 2
#
# Explanation:
#
# The square of side length 4 covers two points points[0] and points[1].
#
# Example 2:
#
# Input: points = [[1,1],[-2,-2],[-2,2]], s = "abb"
#
# Output: 1
#
# Explanation:
#
# The square of side length 2 covers one point, which is points[0].
#
# Example 3:
#
# Input: points = [[1,1],[-1,-1],[2,-2]], s = "ccd"
#
# Output: 0
#
# Explanation:
#
# It's impossible to make any valid squares centered at the origin such
# that it covers only one point among points[0] and points[1].
#
# Constraints:
#
# 1 <= s.length, points.length <= 10^5
#
# points[i].length == 2
#
# -10^9 <= points[i][0], points[i][1] <= 10^9
#
# s.length == points.length
#
# points consists of distinct coordinates.
#
# s consists only of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def maxPointsInsideSquare(self, points: List[List[int]], s: str) -> int:
        """
        Interview explanation:
        Axis-aligned square about origin = Chebyshev ball: include points with
        max(|x|, |y|) <= r. Tags must be unique inside the square.

        Algorithm:
        - For each tag, track the two smallest distances.
        - Max valid r is (global min second-distance) - 1; count points with d <= r.
        - If no tag repeats, all points are valid.

        Complexity: O(n) time, O(|Σ|) space.
        """
        min1: dict[str, int] = {}
        min2: dict[str, int] = {}
        for (x, y), c in zip(points, s):
            d = max(abs(x), abs(y))
            if c not in min1 or d < min1[c]:
                min2[c] = min1.get(c, 10**30)
                min1[c] = d
            elif d < min2.get(c, 10**30):
                min2[c] = d
        limit = min((v for v in min2.values() if v < 10**30), default=10**30)
        if limit == 10**30:
            return len(points)
        return sum(1 for x, y in points if max(abs(x), abs(y)) <= limit - 1)
# @lc code=end
