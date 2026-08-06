#
# @lc app=leetcode id=613 lang=python3
#
# [613] Shortest Distance in a Line
#
# https://leetcode.com/problems/shortest-distance-in-a-line/description/
#
# database
# Easy (79.64%)
# Likes:    345
# Dislikes: 41
# Total Accepted:    86.2K
# Total Submissions: 108.3K
# Testcase Example:  "{\"headers\":{\"Point\":[\"x\"]},\"rows\":{\"Point\":[[-1],[0],[2]]}}"
#
#
# Table: Point
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | x           | int  |
# +-------------+------+
# In SQL, x is the primary key column for this table.
# Each row of this table indicates the position of a point on the X-axis.
#
# Find the shortest distance between any two points from the Point table.
#
# It is guaranteed that the Point table contains at least two rows.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Point table:
# +----+
# | x  |
# +----+
# | -1 |
# | 0  |
# | 2  |
# +----+
# Output:
# +----------+
# | shortest |
# +----------+
# | 1        |
# +----------+
# Explanation: The shortest distance is between points -1 and 0 which is
# |(-1) - 0| = 1.
#
# Follow up: How could you optimize your solution if the Point table is
# ordered in ascending order?
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Shortest absolute distance between two distinct points on a line.

        Algorithm:
        - Self-join distinct x; MIN(ABS(p1.x - p2.x)).

        Complexity: O(N^2) (or O(N log N) with sorted lag).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT MIN(ABS(p1.x - p2.x)) AS shortest
    FROM Point p1
    JOIN Point p2 ON p1.x != p2.x;
    """
# @lc code=end
