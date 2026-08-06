#
# @lc app=leetcode id=3047 lang=python3
#
# [3047] Find the Largest Area of Square Inside Two Rectangles
#
# https://leetcode.com/problems/find-the-largest-area-of-square-inside-two-rectangles/description/
#
# algorithms
# Medium (67.05%)
# Likes:    441
# Dislikes: 86
# Total Accepted:    102.7K
# Total Submissions: 153.2K
# Testcase Example:  "[[1,1],[2,2],[3,1]]\n[[3,3],[4,4],[6,6]]"
#
#
# There exist n rectangles in a 2D plane with edges parallel to the x and
# y axis. You are given two 2D integer arrays bottomLeft and topRight
# where bottomLeft[i] = [a_i, b_i] and topRight[i] = [c_i, d_i] represent
# the bottom-left and top-right coordinates of the i^th rectangle,
# respectively.
#
# You need to find the maximum area of a square that can fit inside the
# intersecting region of at least two rectangles. Return 0 if such a
# square does not exist.
#
# Example 1:
#
# Input: bottomLeft = [[1,1],[2,2],[3,1]], topRight = [[3,3],[4,4],[6,6]]
#
# Output: 1
#
# Explanation:
#
# A square with side length 1 can fit inside either the intersecting
# region of rectangles 0 and 1 or the intersecting region of rectangles 1
# and 2. Hence the maximum area is 1. It can be shown that a square with a
# greater side length can not fit inside any intersecting region of two
# rectangles.
#
# Example 2:
#
# Input: bottomLeft = [[1,1],[1,3],[1,5]], topRight = [[5,5],[5,7],[5,9]]
#
# Output: 4
#
# Explanation:
#
# A square with side length 2 can fit inside either the intersecting
# region of rectangles 0 and 1 or the intersecting region of rectangles 1
# and 2. Hence the maximum area is 2 * 2 = 4. It can be shown that a
# square with a greater side length can not fit inside any intersecting
# region of two rectangles.
#
# Example 3:
#
# Input: bottomLeft = [[1,1],[2,2],[1,2]], topRight = [[3,3],[4,4],[3,4]]
#
# Output: 1
#
# Explanation:
#
# A square with side length 1 can fit inside the intersecting region of
# any two rectangles. Also, no larger square can, so the maximum area is
# 1. Note that the region can be formed by the intersection of more than 2
# rectangles.
#
# Example 4:
#
# Input: bottomLeft = [[1,1],[3,3],[3,1]], topRight = [[2,2],[4,4],[4,2]]
#
# Output: 0
#
# Explanation:
#
# No pair of rectangles intersect, hence, the answer is 0.
#
# Constraints:
#
# n == bottomLeft.length == topRight.length
#
# 2 <= n <= 10^3
#
# bottomLeft[i].length == topRight[i].length == 2
#
# 1 <= bottomLeft[i][0], bottomLeft[i][1] <= 10^7
#
# 1 <= topRight[i][0], topRight[i][1] <= 10^7
#
# bottomLeft[i][0] < topRight[i][0]
#
# bottomLeft[i][1] < topRight[i][1]
#

# @lc code=start
from typing import List


class Solution:
    def largestSquareArea(
        self, bottomLeft: List[List[int]], topRight: List[List[int]]
    ) -> int:
        """
        Interview explanation:
        Max area of an axis-aligned square inside the intersection of some pair
        of rectangles (edges parallel to axes).

        Algorithm:
        - For every pair, intersect boxes; side = min(width, height); area=side^2.
        - n <= 1000 so O(n^2) is fine.

        Complexity: O(n^2) time, O(1) extra space.
        """
        n = len(bottomLeft)
        best = 0
        for i in range(n):
            ax1, ay1 = bottomLeft[i]
            ax2, ay2 = topRight[i]
            for j in range(i + 1, n):
                x1 = max(ax1, bottomLeft[j][0])
                y1 = max(ay1, bottomLeft[j][1])
                x2 = min(ax2, topRight[j][0])
                y2 = min(ay2, topRight[j][1])
                side = min(x2 - x1, y2 - y1)
                if side > 0:
                    best = max(best, side * side)
        return best
# @lc code=end

