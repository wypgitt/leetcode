#
# @lc app=leetcode id=1232 lang=python3
#
# [1232] Check If It Is a Straight Line
#
# https://leetcode.com/problems/check-if-it-is-a-straight-line/description/
#
# algorithms
# Easy (40.23%)
# Likes:    2711
# Dislikes: 296
# Total Accepted:    314K
# Total Submissions: 781K
# Testcase Example:  "[[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]]"
#
# You are given an integer array coordinates, coordinates[i] = [x, y], where
# [x, y] represents the coordinate of a point. Check if these points make a
# straight line in the XY plane.
#
# Example 1:
#
# Input: coordinates = [[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]]
# Output: true
#
# Example 2:
#
# Input: coordinates = [[1,1],[2,2],[3,4],[4,5],[5,6],[7,7]]
# Output: false
#
# Constraints:
#
# 2 <= coordinates.length <= 1000
#
# coordinates[i].length == 2
#
# -10^4 <= coordinates[i][0], coordinates[i][1] <= 10^4
#
# coordinates contains no duplicate point.
#


# @lc code=start
from typing import List

class Solution:
    def checkStraightLine(self, coordinates: List[List[int]]) -> bool:
        """
        Interview explanation:
        Points are colinear iff for every point the cross product of vectors
        (p1-p0) x (pi-p0) is 0 (avoid division/slope).

        Algorithm:
        - dx,dy = p1-p0; for each pi: (xi-x0)*dy == (yi-y0)*dx

        Complexity: O(n) time, O(1) space.
        """
        (x0, y0), (x1, y1) = coordinates[0], coordinates[1]
        dx, dy = x1 - x0, y1 - y0
        for x, y in coordinates[2:]:
            if (x - x0) * dy != (y - y0) * dx:
                return False
        return True
# @lc code=end
