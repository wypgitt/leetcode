#
# @lc app=leetcode id=2153 lang=python3
#
# [2153] The Number of Passengers in Each Bus II
#
# https://leetcode.com/problems/the-number-of-passengers-in-each-bus-ii/description/
#
# database
# Hard (40.47%)
# Likes:    86
# Dislikes: 29
# Total Accepted:    4.1K
# Total Submissions: 10.1K
# Testcase Example:  "{\"headers\":{\"Buses\":[\"bus_id\",\"arrival_time\",\"capacity\"],\"Passengers\":[\"passenger_id\",\"arrival_time\"]},\"rows\":{\"Buses\":[[1,2,1],[2,4,10],[3,7,2]],\"Passengers\":[[11,1],[12,1],[13,5],[14,6],[15,7]]}}"
#
#
# Table: Buses
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | bus_id       | int  |
# | arrival_time | int  |
# | capacity     | int  |
# +--------------+------+
# bus_id contains unique values.
# Each row of this table contains information about the arrival time of a
# bus at the LeetCode station and its capacity (the number of empty seats
# it has).
# No two buses will arrive at the same time and all bus capacities will be
# positive integers.
#
# Table: Passengers
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | passenger_id | int  |
# | arrival_time | int  |
# +--------------+------+
# passenger_id contains unique values.
# Each row of this table contains information about the arrival time of a
# passenger at the LeetCode station.
#
# Buses and passengers arrive at the LeetCode station. If a bus arrives at
# the station at a time t_bus and a passenger arrived at a time
# t_passenger where t_passenger <= t_bus and the passenger did not catch
# any bus, the passenger will use that bus. In addition, each bus has a
# capacity. If at the moment the bus arrives at the station there are more
# passengers waiting than its capacity capacity, only capacity passengers
# will use the bus.
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
# +--------+--------------+----------+
# | bus_id | arrival_time | capacity |
# +--------+--------------+----------+
# | 1      | 2            | 1        |
# | 2      | 4            | 10       |
# | 3      | 7            | 2        |
# +--------+--------------+----------+
# Passengers table:
# +--------------+--------------+
# | passenger_id | arrival_time |
# +--------------+--------------+
# | 11           | 1            |
# | 12           | 1            |
# | 13           | 5            |
# | 14           | 6            |
# | 15           | 7            |
# +--------------+--------------+
# Output:
# +--------+----------------+
# | bus_id | passengers_cnt |
# +--------+----------------+
# | 1      | 1              |
# | 2      | 1              |
# | 3      | 2              |
# +--------+----------------+
# Explanation:
# - Passenger 11 arrives at time 1.
# - Passenger 12 arrives at time 1.
# - Bus 1 arrives at time 2 and collects passenger 11 as it has one empty
# seat.
#
# - Bus 2 arrives at time 4 and collects passenger 12 as it has ten empty
# seats.
#
# - Passenger 12 arrives at time 5.
# - Passenger 13 arrives at time 6.
# - Passenger 14 arrives at time 7.
# - Bus 3 arrives at time 7 and collects passengers 12 and 13 as it has
# two empty seats.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Buses(bus_id, arrival_time, capacity), Passengers(passenger_id,
        arrival_time). Passengers board the earliest bus with arrival >= theirs
        if seats remain (FIFO by arrival). Report passengers_cnt per bus_id.

        Algorithm:
        - Order buses by arrival; for each bus, count newly arrived passengers
          since previous bus plus leftover queue; board min(capacity, waiting);
          carry leftover to next bus (recursive CTE / window simulation).

        Complexity: O(B + P) with ordered scans / recursive CTE.
        """
        return self.sql

    sql = """
    WITH RECURSIVE
    buses_ord AS (
        SELECT
            bus_id,
            arrival_time,
            capacity,
            ROW_NUMBER() OVER (ORDER BY arrival_time) AS rk,
            LAG(arrival_time, 1, -1) OVER (ORDER BY arrival_time) AS prev_time
        FROM Buses
    ),
    new_arrivals AS (
        SELECT
            b.bus_id,
            b.rk,
            b.capacity,
            COUNT(p.passenger_id) AS arrived
        FROM buses_ord b
        LEFT JOIN Passengers p
            ON p.arrival_time > b.prev_time
           AND p.arrival_time <= b.arrival_time
        GROUP BY b.bus_id, b.rk, b.capacity
    ),
    boarded AS (
        SELECT
            bus_id,
            rk,
            LEAST(capacity, arrived) AS passengers_cnt,
            GREATEST(arrived - capacity, 0) AS leftover
        FROM new_arrivals
        WHERE rk = 1
        UNION ALL
        SELECT
            a.bus_id,
            a.rk,
            LEAST(a.capacity, a.arrived + prev.leftover) AS passengers_cnt,
            GREATEST(a.arrived + prev.leftover - a.capacity, 0) AS leftover
        FROM new_arrivals a
        JOIN boarded prev ON a.rk = prev.rk + 1
    )
    SELECT bus_id, passengers_cnt
    FROM boarded
    ORDER BY bus_id;
    """
# @lc code=end
