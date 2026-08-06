#
# @lc app=leetcode id=3061 lang=python3
#
# [3061] Calculate Trapping Rain Water
#
# https://leetcode.com/problems/calculate-trapping-rain-water/description/
#
# database
# Hard (81.59%)
# Likes:    14
# Dislikes: 6
# Total Accepted:    1.8K
# Total Submissions: 2.2K
# Testcase Example:  "{\"headers\":{\"Heights\":[\"id\",\"height\"]},\"rows\":{\"Heights\":[[1,0],[2,1],[3,0],[4,2],[5,1],[6,0],[7,1],[8,3],[9,2],[10,1],[11,2],[12,1]]}}"
#
#
# Table: Heights
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | id          | int  |
# | height      | int  |
# +-------------+------+
# id is the primary key (column with unique values) for this table, and it
# is guaranteed to be in sequential order.
# Each row of this table contains an id and height.
#
# Write a solution to calculate the amount of rainwater can be trapped
# between the bars in the landscape, considering that each bar has a width
# of 1 unit.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Heights table:
# +-----+--------+
# | id  | height |
# +-----+--------+
# | 1   | 0      |
# | 2   | 1      |
# | 3   | 0      |
# | 4   | 2      |
# | 5   | 1      |
# | 6   | 0      |
# | 7   | 1      |
# | 8   | 3      |
# | 9   | 2      |
# | 10  | 1      |
# | 11  | 2      |
# | 12  | 1      |
# +-----+--------+
# Output:
# +---------------------+
# | total_trapped_water |
# +---------------------+
# | 6                   |
# +---------------------+
# Explanation:
#
# The elevation map depicted above (in the black section) is graphically
# represented with the x-axis denoting the id and the y-axis representing
# the heights [0,1,0,2,1,0,1,3,2,1,2,1]. In this scenario, 6 units of
# rainwater are trapped within the blue section.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Heights(id, height) sequential bars of width 1. Total
        trapped rain water (classic trapping-rain-water).

        Algorithm:
        - Window MAX height to the left and right; sum max(0, min(L,R)-h).

        Complexity: O(N).
        """
        self.sql = """
WITH T AS (
    SELECT
        id,
        height,
        MAX(height) OVER (ORDER BY id) AS left_max,
        MAX(height) OVER (ORDER BY id DESC) AS right_max
    FROM Heights
)
SELECT
    SUM(GREATEST(0, LEAST(left_max, right_max) - height)) AS total_trapped_water
FROM T;
"""
        return self.sql
# @lc code=end

