#
# @lc app=leetcode id=2837 lang=python3
#
# [2837] Total Traveled Distance
#
# https://leetcode.com/problems/total-traveled-distance/description/
#
# database
# Easy (76.84%)
# Likes:    18
# Dislikes: 4
# Total Accepted:    6.1K
# Total Submissions: 8K
# Testcase Example:  "{\"headers\":{\"Users\":[\"user_id\",\"name\"],\"Rides\":[\"ride_id\",\"user_id\",\"distance\"]},\"rows\":{\"Users\":[[17,\"Addison\"],[14,\"Ethan\"],[4,\"Michael\"],[2,\"Avery\"],[10,\"Eleanor\"]],\"Rides\":[[72,17,160],[42,14,161],[45,4,59],[32,2,197],[15,4,357],[56,2,196],[10,14,25]]}}"
#
#
# Table: Users
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | user_id     | int     |
# | name        | varchar |
# +-------------+---------+
# user_id is the column with unique values for this table.
# Each row of this table contains user id and name.
#
# Table: Rides
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | ride_id      | int  |
# | user_id      | int  |
# | distance     | int  |
# +--------------+------+
# ride_id is the column of unique values for this table.
# Each row of this table contains ride id, user id, and traveled distance.
#
# Write a solution to calculate the distance traveled by each user. If
# there is a user who hasn't completed any rides, then their distance
# should be considered as 0. Output the user_id, name and total traveled
# distance.
#
# Return the result table ordered by user_id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Users table:
# +---------+---------+
# | user_id | name    |
# +---------+---------+
# | 17      | Addison |
# | 14      | Ethan   |
# | 4       | Michael |
# | 2       | Avery   |
# | 10      | Eleanor |
# +---------+---------+
# Rides table:
# +---------+---------+----------+
# | ride_id | user_id | distance |
# +---------+---------+----------+
# | 72      | 17      | 160      |
# | 42      | 14      | 161      |
# | 45      | 4       | 59       |
# | 32      | 2       | 197      |
# | 15      | 4       | 357      |
# | 56      | 2       | 196      |
# | 10      | 14      | 25       |
# +---------+---------+----------+
# Output:
# +---------+---------+-------------------+
# | user_id | name    | traveled distance |
# +---------+---------+-------------------+
# | 2       | Avery   | 393               |
# | 4       | Michael | 416               |
# | 10      | Eleanor | 0                 |
# | 14      | Ethan   | 186               |
# | 17      | Addison | 160               |
# +---------+---------+-------------------+
# Explanation:
# -  User id 2 completed two journeys of 197 and 196, resulting in a
# combined travel distance of 393.
# -  User id 4 completed two journeys of 59 and 357, resulting in a
# combined travel distance of 416.
# -  User id 14 completed two journeys of 161 and 25, resulting in a
# combined travel distance of 186.
# -  User id 16 completed only one journey of 160.
# -  User id 10 did not complete any journeys, thus the total travel
# distance remains at 0.
# Returning the table orderd by user_id in ascending order.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Users(user_id, name), Rides(ride_id, user_id, distance).
        For each user return total traveled distance (0 if no rides).

        Algorithm:
        - LEFT JOIN Users to Rides; SUM(distance) with IFNULL; GROUP BY user;
          ORDER BY user_id.

        Complexity: O(N) join/aggregate.
        """
        self.sql = """
SELECT
    user_id,
    name,
    IFNULL(SUM(distance), 0) AS `traveled distance`
FROM Users
LEFT JOIN Rides USING (user_id)
GROUP BY 1
ORDER BY 1;
"""
        return self.sql
# @lc code=end
