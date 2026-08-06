#
# @lc app=leetcode id=1637 lang=python3
#
# [1637] Widest Vertical Area Between Two Points Containing No Points
#
# https://leetcode.com/problems/widest-vertical-area-between-two-points-containing-no-points/description/
#
# algorithms
# Easy (87.12%)
# Likes:    991
# Dislikes: 1795
# Total Accepted:    205K
# Total Submissions: 236K
# Testcase Example:  "[[8,7],[9,9],[7,4],[9,7]]"
#
# Given n points on a 2D plane where points[i] = [x_i, y_i], Return the widest
# vertical area between two points such that no points are inside the area.
#
# A vertical area is an area of fixed-width extending infinitely along the
# y-axis (i.e., infinite height). The widest vertical area is the one with the
# maximum width.
#
# Note that points on the edge of a vertical area are not considered included
# in the area.
#
# Example 1:
#
# Input: points = [[8,7],[9,9],[7,4],[9,7]]
# Output: 1
# Explanation: Both the red and the blue area are optimal.
#
# Example 2:
#
# Input: points = [[3,1],[9,0],[1,0],[1,4],[5,3],[8,8]]
# Output: 3
#
# Constraints:
#
# n == points.length
#
# 2 <= n <= 10^5
#
# points[i].length == 2
#
# 0 <= x_i, y_i <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maxWidthOfVerticalArea(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Widest gap between consecutive distinct x-coordinates (vertical area empty).

        Algorithm (sort x):
        - Sort unique/ all x; max adjacent difference.

        Complexity: O(n log n) time, O(n) space.
        """
        xs = sorted(x for x, _ in points)
        return max(xs[i] - xs[i - 1] for i in range(1, len(xs)))

    def maxWidthOfVerticalArea_unique(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: dedupe x then sort (same gaps; zero gaps removed).

        Algorithm:
        - sorted(set(x)); max adjacent diff (0 if <2).

        Complexity: O(n log n).
        """
        xs = sorted({x for x, _ in points})
        if len(xs) < 2:
            return 0
        return max(xs[i] - xs[i - 1] for i in range(1, len(xs)))
# @lc code=end
