#
# @lc app=leetcode id=1459 lang=python3
#
# [1459] Rectangles Area
#
# https://leetcode.com/problems/rectangles-area/description/
#
# database
# Medium (68.79%)
# Likes:    99
# Dislikes: 162
# Total Accepted:    20.4K
# Total Submissions: 29.7K
# Testcase Example:  "{\"headers\":{\"Points\":[\"id\",\"x_value\",\"y_value\"]},\"rows\":{\"Points\":[[1,2,7],[2,4,8],[3,2,10]]}}"
#
#
# Table: Points
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | id            | int     |
# | x_value       | int     |
# | y_value       | int     |
# +---------------+---------+
# id is the column with unique values for this table.
# Each point is represented as a 2D coordinate (x_value, y_value).
#
# Write a solution to report all possible axis-aligned rectangles with a
# non-zero area that can be formed by any two points from the Points
# table.
#
# Each row in the result should contain three columns (p1, p2, area)
# where:
#
# p1 and p2 are the id's of the two points that determine the opposite
# corners of a rectangle.
#
# area is the area of the rectangle and must be non-zero.
#
# Return the result table ordered by area in descending order. If there is
# a tie, order them by p1 in ascending order. If there is still a tie,
# order them by p2 in ascending order.
#
# The result format is in the following table.
#
# Example 1:
#
# Input:
# Points table:
# +----------+-------------+-------------+
# | id       | x_value     | y_value     |
# +----------+-------------+-------------+
# | 1        | 2           | 7           |
# | 2        | 4           | 8           |
# | 3        | 2           | 10          |
# +----------+-------------+-------------+
# Output:
# +----------+-------------+-------------+
# | p1       | p2          | area        |
# +----------+-------------+-------------+
# | 2        | 3           | 4           |
# | 1        | 2           | 2           |
# +----------+-------------+-------------+
# Explanation:
# The rectangle formed by p1 = 2 and p2 = 3 has an area equal to |4-2| *
# |8-10| = 4.
# The rectangle formed by p1 = 1 and p2 = 2 has an area equal to |2-4| *
# |7-8| = 2.
# Note that the rectangle formed by p1 = 1 and p2 = 3 is invalid because
# the area is 0.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Points(id, x_value, y_value). Find all axis-aligned
        rectangles from 4 distinct points; return p1, p2 (diagonal corners
        with p1.x < p2.x and p1.y > p2.y) and area, ordered by area DESC,
        p1 ASC, p2 ASC. Only area > 0.

        Algorithm:
        - Cross join Points a,b where a.x < b.x and a.y > b.y; require the
          other two corners exist; area = (b.x-a.x)*(a.y-b.y).

        Complexity: O(P^2) joins with lookups.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT a.id AS p1, b.id AS p2,
           ABS(a.x_value - b.x_value) * ABS(a.y_value - b.y_value) AS area
    FROM Points a
    JOIN Points b ON a.x_value < b.x_value AND a.y_value > b.y_value
    WHERE EXISTS (
        SELECT 1 FROM Points c
        WHERE c.x_value = a.x_value AND c.y_value = b.y_value
    )
    AND EXISTS (
        SELECT 1 FROM Points d
        WHERE d.x_value = b.x_value AND d.y_value = a.y_value
    )
    AND ABS(a.x_value - b.x_value) * ABS(a.y_value - b.y_value) > 0
    ORDER BY area DESC, p1 ASC, p2 ASC;
    """
# @lc code=end
