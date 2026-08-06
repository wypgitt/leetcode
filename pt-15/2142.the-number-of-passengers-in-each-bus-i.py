#
# @lc app=leetcode id=2142 lang=python3
#
# [2142] The Number of Passengers in Each Bus I
#
# https://leetcode.com/problems/the-number-of-passengers-in-each-bus-i/description/
#
# database
# Medium (49.13%)
# Likes:    118
# Dislikes: 12
# Total Accepted:    12.4K
# Total Submissions: 25.3K
# Testcase Example:  "{\"headers\":{\"Buses\":[\"bus_id\",\"arrival_time\"],\"Passengers\":[\"passenger_id\",\"arrival_time\"]},\"rows\":{\"Buses\":[[1,2],[2,4],[3,7]],\"Passengers\":[[11,1],[12,5],[13,6],[14,7]]}}"
#
#
# Table: Buses
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | bus_id       | int  |
# | arrival_time | int  |
# +--------------+------+
# bus_id is the column with unique values for this table.
# Each row of this table contains information about the arrival time of a
# bus at the LeetCode station.
# No two buses will arrive at the same time.
#
# Table: Passengers
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | passenger_id | int  |
# | arrival_time | int  |
# +--------------+------+
# passenger_id is the column with unique values for this table.
# Each row of this table contains information about the arrival time of a
# passenger at the LeetCode station.
#
# Buses and passengers arrive at the LeetCode station. If a bus arrives at
# the station at time t_bus and a passenger arrived at time t_passenger
# where t_passenger <= t_bus and the passenger did not catch any bus, the
# passenger will use that bus.
#
# Write a solution to report the number of users that used each bus.
#
# Return the result table ordered by bus_id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Buses table:
# +--------+--------------+
# | bus_id | arrival_time |
# +--------+--------------+
# | 1      | 2            |
# | 2      | 4            |
# | 3      | 7            |
# +--------+--------------+
# Passengers table:
# +--------------+--------------+
# | passenger_id | arrival_time |
# +--------------+--------------+
# | 11           | 1            |
# | 12           | 5            |
# | 13           | 6            |
# | 14           | 7            |
# +--------------+--------------+
# Output:
# +--------+----------------+
# | bus_id | passengers_cnt |
# +--------+----------------+
# | 1      | 1              |
# | 2      | 0              |
# | 3      | 3              |
# +--------+----------------+
# Explanation:
# - Passenger 11 arrives at time 1.
# - Bus 1 arrives at time 2 and collects passenger 11.
#
# - Bus 2 arrives at time 4 and does not collect any passengers.
#
# - Passenger 12 arrives at time 5.
# - Passenger 13 arrives at time 6.
# - Passenger 14 arrives at time 7.
# - Bus 3 arrives at time 7 and collects passengers 12, 13, and 14.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL premium: Buses(bus_id, arrival_time), Passengers(passenger_id,
        arrival_time). Each passenger takes the earliest bus with
        bus.arrival_time >= passenger.arrival_time. Count passengers per bus
        (0 if none). Buses have distinct arrival times.

        Algorithm:
        - LAG previous bus time; LEFT JOIN passengers in (prev, cur]; GROUP BY bus.

        Complexity: O(B log B + P) with joins/windows.
        """
        return self.sql

    sql = """
    WITH BusesNeighbors AS (
        SELECT
            bus_id,
            arrival_time,
            IFNULL(LAG(arrival_time) OVER (ORDER BY arrival_time), 0) AS prev_arrival_time
        FROM Buses
    )
    SELECT
        BusesNeighbors.bus_id,
        COUNT(Passengers.passenger_id) AS passengers_cnt
    FROM BusesNeighbors
    LEFT JOIN Passengers
      ON BusesNeighbors.prev_arrival_time < Passengers.arrival_time
     AND Passengers.arrival_time <= BusesNeighbors.arrival_time
    GROUP BY BusesNeighbors.bus_id
    ORDER BY BusesNeighbors.bus_id;
    """
# @lc code=end

