#
# @lc app=leetcode id=612 lang=python3
#
# [612] Shortest Distance in a Plane
#
# https://leetcode.com/problems/shortest-distance-in-a-plane/description/
#
# database
# Medium (60.92%)
# Likes:    226
# Dislikes: 72
# Total Accepted:    49.5K
# Total Submissions: 81.2K
# Testcase Example:  "{\"headers\":{\"Point2D\":[\"x\",\"y\"]},\"rows\":{\"Point2D\":[[-1,-1],[0,0],[-1,-2]]}}"
#
#
# Table: Point2D
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | x           | int  |
# | y           | int  |
# +-------------+------+
# (x, y) is the primary key column (combination of columns with unique
# values) for this table.
# Each row of this table indicates the position of a point on the X-Y
# plane.
#
# The distance between two points p_1(x_1, y_1) and p_2(x_2, y_2) is
# sqrt((x_2 - x_1)^2 + (y_2 - y_1)^2).
#
# Write a solution to report the shortest distance between any two points
# from the Point2D table. Round the distance to two decimal points.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Point2D table:
# +----+----+
# | x  | y  |
# +----+----+
# | -1 | -1 |
# | 0  | 0  |
# | -1 | -2 |
# +----+----+
# Output:
# +----------+
# | shortest |
# +----------+
# | 1.00     |
# +----------+
# Explanation: The shortest distance is 1.00 from point (-1, -1) to (-1,
# 2).
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Shortest Euclidean distance between two distinct points on a plane.

        Algorithm:
        - Cross join distinct pairs; MIN of SQRT((x1-x2)^2+(y1-y2)^2); ROUND to 2 decimals.

        Complexity: O(N^2) pairs.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT ROUND(MIN(SQRT(POW(p1.x - p2.x, 2) + POW(p1.y - p2.y, 2))), 2) AS shortest
    FROM Point2D p1
    JOIN Point2D p2
      ON p1.x != p2.x OR p1.y != p2.y;
    """
# @lc code=end
