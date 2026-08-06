#
# @lc app=leetcode id=2238 lang=python3
#
# [2238] Number of Times a Driver Was a Passenger
#
# https://leetcode.com/problems/number-of-times-a-driver-was-a-passenger/description/
#
# database
# Medium (71.69%)
# Likes:    73
# Dislikes: 6
# Total Accepted:    11.6K
# Total Submissions: 16.2K
# Testcase Example:  "{\"headers\":{\"Rides\":[\"ride_id\",\"driver_id\",\"passenger_id\"]},\"rows\":{\"Rides\":[[1,7,1],[2,7,2],[3,11,1],[4,11,7],[5,11,7],[6,11,3]]}}"
#
#
# Table: Rides
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | ride_id      | int  |
# | driver_id    | int  |
# | passenger_id | int  |
# +--------------+------+
# ride_id is the column with unique values for this table.
# Each row of this table contains the ID of the driver and the ID of the
# passenger that rode in ride_id.
# Note that driver_id != passenger_id.
#
# Write a solution to report the ID of each driver and the number of times
# they were a passenger.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Rides table:
# +---------+-----------+--------------+
# | ride_id | driver_id | passenger_id |
# +---------+-----------+--------------+
# | 1       | 7         | 1            |
# | 2       | 7         | 2            |
# | 3       | 11        | 1            |
# | 4       | 11        | 7            |
# | 5       | 11        | 7            |
# | 6       | 11        | 3            |
# +---------+-----------+--------------+
# Output:
# +-----------+-----+
# | driver_id | cnt |
# +-----------+-----+
# | 7         | 2   |
# | 11        | 0   |
# +-----------+-----+
# Explanation:
# There are two drivers in all the given rides: 7 and 11.
# The driver with ID = 7 was a passenger two times.
# The driver with ID = 11 was never a passenger.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL premium. Rides(ride_id, driver_id, passenger_id). For each driver who
        drove at least once, count how many times they appear as a passenger.

        Algorithm:
        - Distinct drivers LEFT JOIN rides on passenger_id; GROUP BY driver_id.

        Complexity: O(N).
        """
        self.sql = """
SELECT d.driver_id, COUNT(r.ride_id) AS cnt
FROM (SELECT DISTINCT driver_id FROM Rides) d
LEFT JOIN Rides r ON d.driver_id = r.passenger_id
GROUP BY d.driver_id;
"""
        return self.sql
# @lc code=end
