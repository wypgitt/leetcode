#
# @lc app=leetcode id=1037 lang=python3
#
# [1037] Valid Boomerang
#
# https://leetcode.com/problems/valid-boomerang/description/
#
# algorithms
# Easy (40.04%)
# Likes:    475
# Dislikes: 545
# Total Accepted:    80.1K
# Total Submissions: 200K
# Testcase Example:  "[[1,1],[2,3],[3,2]]"
#
# Given an array points where points[i] = [x_i, y_i] represents a point on the
# X-Y plane, return true if these points are a boomerang.
#
# A boomerang is a set of three points that are all distinct and not in a
# straight line.
#
# Example 1:
#
# Input: points = [[1,1],[2,3],[3,2]]
# Output: true
#
# Example 2:
#
# Input: points = [[1,1],[2,2],[3,3]]
# Output: false
#
# Constraints:
#
# points.length == 3
#
# points[i].length == 2
#
# 0 <= x_i, y_i <= 100
#

# @lc code=start
from typing import List


class Solution:
    def isBoomerang(self, points: List[List[int]]) -> bool:
        """
        Interview explanation:
        Three points form a boomerang iff not collinear (and thus distinct).
        Cross product of vectors AB and AC nonzero: (b-a)×(c-a) != 0.

        Algorithm:
        - (x1,y1),(x2,y2),(x3,y3)
        - Return (x2-x1)*(y3-y1) - (x3-x1)*(y2-y1) != 0

        Complexity: O(1) time and space.
        """
        (x1, y1), (x2, y2), (x3, y3) = points
        return (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1) != 0
# @lc code=end
