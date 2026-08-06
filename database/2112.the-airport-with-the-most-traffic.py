#
# @lc app=leetcode id=2112 lang=python3
#
# [2112] The Airport With the Most Traffic
#
# https://leetcode.com/problems/the-airport-with-the-most-traffic/description/
#
# database
# Medium (71.71%)
# Likes:    73
# Dislikes: 8
# Total Accepted:    12.4K
# Total Submissions: 17.2K
# Testcase Example:  "{\"headers\":{\"Flights\":[\"departure_airport\",\"arrival_airport\",\"flights_count\"]},\"rows\":{\"Flights\":[[1,2,4],[2,1,5],[2,4,5]]}}"
#
#
# Table: Flights
#
# +-------------------+------+
# | Column Name       | Type |
# +-------------------+------+
# | departure_airport | int  |
# | arrival_airport   | int  |
# | flights_count     | int  |
# +-------------------+------+
# (departure_airport, arrival_airport) is the primary key column
# (combination of columns with unique values) for this table.
# Each row of this table indicates that there were flights_count flights
# that departed from departure_airport and arrived at arrival_airport.
#
# Write a solution to report the ID of the airport with the most traffic.
# The airport with the most traffic is the airport that has the largest
# total number of flights that either departed from or arrived at the
# airport. If there is more than one airport with the most traffic, report
# them all.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Flights table:
# +-------------------+-----------------+---------------+
# | departure_airport | arrival_airport | flights_count |
# +-------------------+-----------------+---------------+
# | 1                 | 2               | 4             |
# | 2                 | 1               | 5             |
# | 2                 | 4               | 5             |
# +-------------------+-----------------+---------------+
# Output:
# +------------+
# | airport_id |
# +------------+
# | 2          |
# +------------+
# Explanation:
# Airport 1 was engaged with 9 flights (4 departures, 5 arrivals).
# Airport 2 was engaged with 14 flights (10 departures, 4 arrivals).
# Airport 4 was engaged with 5 flights (5 arrivals).
# The airport with the most traffic is airport 2.
#
# Example 2:
#
# Input:
# Flights table:
# +-------------------+-----------------+---------------+
# | departure_airport | arrival_airport | flights_count |
# +-------------------+-----------------+---------------+
# | 1                 | 2               | 4             |
# | 2                 | 1               | 5             |
# | 3                 | 4               | 5             |
# | 4                 | 3               | 4             |
# | 5                 | 6               | 7             |
# +-------------------+-----------------+---------------+
# Output:
# +------------+
# | airport_id |
# +------------+
# | 1          |
# | 2          |
# | 3          |
# | 4          |
# +------------+
# Explanation:
# Airport 1 was engaged with 9 flights (4 departures, 5 arrivals).
# Airport 2 was engaged with 9 flights (5 departures, 4 arrivals).
# Airport 3 was engaged with 9 flights (5 departures, 4 arrivals).
# Airport 4 was engaged with 9 flights (4 departures, 5 arrivals).
# Airport 5 was engaged with 7 flights (7 departures).
# Airport 6 was engaged with 7 flights (7 arrivals).
# The airports with the most traffic are airports 1, 2, 3, and 4.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL premium: Flights(departure_airport, arrival_airport, flights_count).
        Airport traffic = sum of flights_count as departure or arrival. Return
        airport_id(s) with maximum traffic.

        Algorithm:
        - UNION ALL dep/arr counts; GROUP BY airport; RANK by SUM DESC; filter rank=1.

        Complexity: O(N) over flight rows.
        """
        return self.sql

    sql = """
    WITH AirportToCount AS (
        SELECT departure_airport AS airport_id, flights_count
        FROM Flights
        UNION ALL
        SELECT arrival_airport, flights_count
        FROM Flights
    ),
    RankedAirports AS (
        SELECT
            airport_id,
            RANK() OVER (ORDER BY SUM(flights_count) DESC) AS rnk
        FROM AirportToCount
        GROUP BY airport_id
    )
    SELECT airport_id
    FROM RankedAirports
    WHERE rnk = 1;
    """
# @lc code=end

