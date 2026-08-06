#
# @lc app=leetcode id=836 lang=python3
#
# [836] Rectangle Overlap
#
# https://leetcode.com/problems/rectangle-overlap/description/
#
# algorithms
# Easy (46.95%)
# Likes:    2103
# Dislikes: 483
# Total Accepted:    189K
# Total Submissions: 402K
# Testcase Example:  "[0,0,2,2]"
#
# An axis-aligned rectangle is represented as a list [x1, y1, x2, y2], where
# (x1, y1) is the coordinate of its bottom-left corner, and (x2, y2) is the
# coordinate of its top-right corner. Its top and bottom edges are parallel to
# the X-axis, and its left and right edges are parallel to the Y-axis.
#
# Two rectangles overlap if the area of their intersection is positive. To be
# clear, two rectangles that only touch at the corner or edges do not overlap.
#
# Given two axis-aligned rectangles rec1 and rec2, return true if they overlap,
# otherwise return false.
#
# Example 1:
#
# Input: rec1 = [0,0,2,2], rec2 = [1,1,3,3]
# Output: true
#
# Example 2:
#
# Input: rec1 = [0,0,1,1], rec2 = [1,0,2,1]
# Output: false
#
# Example 3:
#
# Input: rec1 = [0,0,1,1], rec2 = [2,2,3,3]
# Output: false
#
# Constraints:
#
# rec1.length == 4
#
# rec2.length == 4
#
# -10^9 <= rec1[i], rec2[i] <= 10^9
#
# rec1 and rec2 represent a valid rectangle with a non-zero area.
#

# @lc code=start

from typing import List


class Solution:
    def isRectangleOverlap(self, rec1: List[int], rec2: List[int]) -> bool:
        """
        Interview explanation:
        Axis-aligned rectangles overlap iff projections overlap on both X and Y
        (not just touch on edge for this problem — area overlap required).

        Algorithm:
        - Not overlap if one fully left/right/above/below the other.
        - Equivalent: max(x1)<min(x2) and max(y1)<min(y2) for intervals.

        Complexity: O(1) time/space.
        """
        return not (
            rec1[2] <= rec2[0]
            or rec2[2] <= rec1[0]
            or rec1[3] <= rec2[1]
            or rec2[3] <= rec1[1]
        )

    def isRectangleOverlap_projection(self, rec1: List[int], rec2: List[int]) -> bool:
        """
        Interview explanation:
        Positive-area overlap of interval projections on both axes.

        Algorithm:
        - dx = min(x2)-max(x1); dy = min(y2)-max(y1); return dx>0 and dy>0.

        Complexity: O(1).
        """
        dx = min(rec1[2], rec2[2]) - max(rec1[0], rec2[0])
        dy = min(rec1[3], rec2[3]) - max(rec1[1], rec2[1])
        return dx > 0 and dy > 0
# @lc code=end
