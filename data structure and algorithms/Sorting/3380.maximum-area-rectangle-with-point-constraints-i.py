#
# @lc app=leetcode id=3380 lang=python3
#
# [3380] Maximum Area Rectangle With Point Constraints I
#
# https://leetcode.com/problems/maximum-area-rectangle-with-point-constraints-i/description/
#
# algorithms
# Medium (52.31%)
# Likes:    86
# Dislikes: 20
# Total Accepted:    16.8K
# Total Submissions: 32.1K
# Testcase Example:  "[[1,1],[1,3],[3,1],[3,3]]"
#
#
# You are given an array points where points[i] = [x_i, y_i] represents
# the coordinates of a point on an infinite plane.
#
# Your task is to find the maximum area of a rectangle that:
#
# Can be formed using four of these points as its corners.
#
# Does not contain any other point inside or on its border.
#
# Has its edges parallel to the axes.
#
# Return the maximum area that you can obtain or -1 if no such rectangle
# is possible.
#
# Example 1:
#
# Input: points = [[1,1],[1,3],[3,1],[3,3]]
#
# Output: 4
#
# Explanation:
#
# We can make a rectangle with these 4 points as corners and there is no
# other point that lies inside or on the border. Hence, the maximum
# possible area would be 4.
#
# Example 2:
#
# Input: points = [[1,1],[1,3],[3,1],[3,3],[2,2]]
#
# Output: -1
#
# Explanation:
#
# There is only one rectangle possible is with points [1,1], [1,3], [3,1]
# and [3,3] but [2,2] will always lie inside it. Hence, returning -1.
#
# Example 3:
#
# Input: points = [[1,1],[1,3],[3,1],[3,3],[1,2],[3,2]]
#
# Output: 2
#
# Explanation:
#
# The maximum area rectangle is formed by the points [1,3], [1,2], [3,2],
# [3,3], which has an area of 2. Additionally, the points [1,1], [1,2],
# [3,1], [3,2] also form a valid rectangle with the same area.
#
# Constraints:
#
# 1 <= points.length <= 10
#
# points[i].length == 2
#
# 0 <= x_i, y_i <= 100
#
# All the given points are unique.
#

# @lc code=start
from typing import List


class Solution:
    def maxRectangleArea(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Axis-aligned empty rectangle from four given corners. n <= 10 => try all
        diagonal pairs.

        Algorithm:
        - For each pair as opposite corners, check the other two corners exist.
        - Reject if any other point lies inside or on the border.
        - Track max area.

        Complexity: O(n^3) time, O(n) space.
        """
        pts = {(x, y) for x, y in points}
        ans = -1
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            for j in range(i + 1, n):
                x2, y2 = points[j]
                if x1 == x2 or y1 == y2:
                    continue
                if (x1, y2) not in pts or (x2, y1) not in pts:
                    continue
                minx, maxx = min(x1, x2), max(x1, x2)
                miny, maxy = min(y1, y2), max(y1, y2)
                corners = {(x1, y1), (x1, y2), (x2, y1), (x2, y2)}
                if any(
                    minx <= x <= maxx
                    and miny <= y <= maxy
                    and (x, y) not in corners
                    for x, y in pts
                ):
                    continue
                ans = max(ans, (maxx - minx) * (maxy - miny))
        return ans
# @lc code=end
