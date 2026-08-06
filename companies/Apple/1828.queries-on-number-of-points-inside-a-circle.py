#
# @lc app=leetcode id=1828 lang=python3
#
# [1828] Queries on Number of Points Inside a Circle
#
# https://leetcode.com/problems/queries-on-number-of-points-inside-a-circle/description/
#
# algorithms
# Medium (86.85%)
# Likes:    1203
# Dislikes: 90
# Total Accepted:    98.9K
# Total Submissions: 114K
# Testcase Example:  "[[1,3],[3,3],[5,3],[2,2]]"
#
# You are given an array points where points[i] = [x_i, y_i] is the coordinates
# of the i^th point on a 2D plane. Multiple points can have the same
# coordinates.
#
# You are also given an array queries where queries[j] = [x_j, y_j, r_j]
# describes a circle centered at (x_j, y_j) with a radius of r_j.
#
# For each query queries[j], compute the number of points inside the j^th
# circle. Points on the border of the circle are considered inside.
#
# Return an array answer, where answer[j] is the answer to the j^th query.
#
# Example 1:
#
# Input: points = [[1,3],[3,3],[5,3],[2,2]], queries =
# [[2,3,1],[4,3,1],[1,1,2]]
# Output: [3,2,2]
# Explanation: The points and circles are shown above.
# queries[0] is the green circle, queries[1] is the red circle, and queries[2]
# is the blue circle.
#
# Example 2:
#
# Input: points = [[1,1],[2,2],[3,3],[4,4],[5,5]], queries =
# [[1,2,2],[2,2,2],[4,3,2],[4,3,3]]
# Output: [2,3,2,4]
# Explanation: The points and circles are shown above.
# queries[0] is green, queries[1] is red, queries[2] is blue, and queries[3] is
# purple.
#
# Constraints:
#
# 1 <= points.length <= 500
#
# points[i].length == 2
#
# 0 <= x_i, y_i <= 500
#
# 1 <= queries.length <= 500
#
# queries[j].length == 3
#
# 0 <= x_j, y_j <= 500
#
# 1 <= r_j <= 500
#
# All coordinates are integers.
#
# Follow up: Could you find the answer for each query in better complexity than
# O(n)?
#

# @lc code=start
from typing import List


class Solution:
    def countPoints(self, points: List[List[int]], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        For each query circle (x,y,r), count points with (px-x)^2+(py-y)^2 <= r^2.

        Algorithm (brute):
        - For each query, scan all points; compare squared distances.

        Complexity: O(Q*P) time, O(1) extra — optimal for constraints (~500^2).
        """
        ans = []
        for x, y, r in queries:
            r2 = r * r
            ans.append(sum((px - x) ** 2 + (py - y) ** 2 <= r2 for px, py in points))
        return ans
# @lc code=end
