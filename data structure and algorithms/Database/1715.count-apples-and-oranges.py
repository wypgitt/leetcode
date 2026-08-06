#
# @lc app=leetcode id=1715 lang=python3
#
# [1715] Count Apples and Oranges
#
# https://leetcode.com/problems/count-apples-and-oranges/description/
#
# database
# Medium (75.76%)
# Likes:    91
# Dislikes: 22
# Total Accepted:    19.6K
# Total Submissions: 25.9K
# Testcase Example:  "{\"headers\":{\"Boxes\":[\"box_id\",\"chest_id\",\"apple_count\",\"orange_count\"],\"Chests\":[\"chest_id\",\"apple_count\",\"orange_count\"]},\"rows\":{\"Boxes\":[[2,null,6,15],[18,14,4,15],[19,3,8,4],[12,2,19,20],[20,6,12,9],[8,6,9,9],[3,14,16,7]],\"Chests\":[[6,5,6],[14,20,10],[2,8,8],[3,19,4],[16,19,19]]}}"
#
#
# Table: Boxes
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | box_id       | int  |
# | chest_id     | int  |
# | apple_count  | int  |
# | orange_count | int  |
# +--------------+------+
# box_id is the column with unique values for this table.
# chest_id is a foreign key (reference column) of the chests table.
# This table contains information about the boxes and the number of
# oranges and apples they have. Each box may include a chest, which also
# can contain oranges and apples.
#
# Table: Chests
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | chest_id     | int  |
# | apple_count  | int  |
# | orange_count | int  |
# +--------------+------+
# chest_id is the column with unique values for this table.
# This table contains information about the chests and the corresponding
# number of oranges and apples they have.
#
# Write a solution to count the number of apples and oranges in all the
# boxes. If a box contains a chest, you should also include the number of
# apples and oranges it has.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Boxes table:
# +--------+----------+-------------+--------------+
# | box_id | chest_id | apple_count | orange_count |
# +--------+----------+-------------+--------------+
# | 2      | null     | 6           | 15           |
# | 18     | 14       | 4           | 15           |
# | 19     | 3        | 8           | 4            |
# | 12     | 2        | 19          | 20           |
# | 20     | 6        | 12          | 9            |
# | 8      | 6        | 9           | 9            |
# | 3      | 14       | 16          | 7            |
# +--------+----------+-------------+--------------+
# Chests table:
# +----------+-------------+--------------+
# | chest_id | apple_count | orange_count |
# +----------+-------------+--------------+
# | 6        | 5           | 6            |
# | 14       | 20          | 10           |
# | 2        | 8           | 8            |
# | 3        | 19          | 4            |
# | 16       | 19          | 19           |
# +----------+-------------+--------------+
# Output:
# +-------------+--------------+
# | apple_count | orange_count |
# +-------------+--------------+
# | 151         | 123          |
# +-------------+--------------+
# Explanation:
# box 2 has 6 apples and 15 oranges.
# box 18 has 4 + 20 (from the chest) = 24 apples and 15 + 10 (from the
# chest) = 25 oranges.
# box 19 has 8 + 19 (from the chest) = 27 apples and 4 + 4 (from the
# chest) = 8 oranges.
# box 12 has 19 + 8 (from the chest) = 27 apples and 20 + 8 (from the
# chest) = 28 oranges.
# box 20 has 12 + 5 (from the chest) = 17 apples and 9 + 6 (from the
# chest) = 15 oranges.
# box 8 has 9 + 5 (from the chest) = 14 apples and 9 + 6 (from the chest)
# = 15 oranges.
# box 3 has 16 + 20 (from the chest) = 36 apples and 7 + 10 (from the
# chest) = 17 oranges.
# Total number of apples = 6 + 24 + 27 + 27 + 17 + 14 + 36 = 151
# Total number of oranges = 15 + 25 + 8 + 28 + 15 + 15 + 17 = 123
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Count total apples and oranges across boxes, including apples/
        oranges stored in chests that contain boxes (Boxes join Chests).

        Algorithm:
        - SUM(b.apple_count + IFNULL(c.apple_count,0)) and same for orange
          FROM Boxes b LEFT JOIN Chests c ON b.chest_id = c.chest_id.

        Complexity: O(N) scan/join.
        """
        return self.sql

    sql = """
    SELECT
        SUM(b.apple_count + IFNULL(c.apple_count, 0)) AS apple_count,
        SUM(b.orange_count + IFNULL(c.orange_count, 0)) AS orange_count
    FROM Boxes b
    LEFT JOIN Chests c ON b.chest_id = c.chest_id;
    """
# @lc code=end
