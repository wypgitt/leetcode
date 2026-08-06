#
# @lc app=leetcode id=610 lang=python3
#
# [610] Triangle Judgement
#
# https://leetcode.com/problems/triangle-judgement/description/
#
# algorithms
# Easy (75.05%)
# Likes:    892
# Dislikes: 242
# Total Accepted:    523K
# Total Submissions: 696K
# Testcase Example:  "{\"headers\":{\"Triangle\":[\"x\",\"y\",\"z\"]},\"rows\":{\"Triangle\":[[13,15,30],[10,20,15]]}}"
#
# Table: Triangle
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | x | int |
# | y | int |
# | z | int |
# +-------------+------+
# In SQL, (x, y, z) is the primary key column for this table.
# Each row of this table contains the lengths of three line segments.
#
# Report for every three line segments whether they can form a triangle.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Triangle table:
# +----+----+----+
# | x | y | z |
# +----+----+----+
# | 13 | 15 | 30 |
# | 10 | 20 | 15 |
# +----+----+----+
# Output:
# +----+----+----+----------+
# | x | y | z | triangle |
# +----+----+----+----------+
# | 13 | 15 | 30 | No |
# | 10 | 20 | 15 | Yes |
# +----+----+----+----------+
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        A triangle exists iff the three sides satisfy the triangle inequalities.

        Algorithm:
        - CASE WHEN x+y>z AND x+z>y AND y+z>x THEN 'Yes' ELSE 'No'.

        Complexity: O(N).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        x, y, z,
        CASE
            WHEN x + y > z AND x + z > y AND y + z > x THEN 'Yes'
            ELSE 'No'
        END AS triangle
    FROM Triangle;
    """
# @lc code=end
