#
# @lc app=leetcode id=1294 lang=python3
#
# [1294] Weather Type in Each Country
#
# https://leetcode.com/problems/weather-type-in-each-country/description/
#
# database
# Easy (67.11%)
# Likes:    147
# Dislikes: 30
# Total Accepted:    46.3K
# Total Submissions: 69K
# Testcase Example:  "{\"headers\":{\"Countries\":[\"country_id\",\"country_name\"],\"Weather\":[\"country_id\",\"weather_state\",\"day\"]},\"rows\":{\"Countries\":[[2,\"USA\"],[3,\"Australia\"],[7,\"Peru\"],[5,\"China\"],[8,\"Morocco\"],[9,\"Spain\"]],\"Weather\":[[2,15,\"2019-11-01\"],[2,12,\"2019-10-28\"],[2,12,\"2019-10-27\"],[3,-2,\"2019-11-10\"],[3,0,\"2019-11-11\"],[3,3,\"2019-11-12\"],[5,16,\"2019-11-07\"],[5,18,\"2019-11-09\"],[5,21,\"2019-11-23\"],[7,25,\"2019-11-28\"],[7,22,\"2019-12-01\"],[7,20,\"2019-12-02\"],[8,25,\"2019-11-05\"],[8,27,\"2019-11-15\"],[8,31,\"2019-11-25\"],[9,7,\"2019-10-23\"],[9,3,\"2019-12-23\"]]}}"
#
#
# Table: Countries
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | country_id    | int     |
# | country_name  | varchar |
# +---------------+---------+
# country_id is the primary key (column with unique values) for this
# table.
# Each row of this table contains the ID and the name of one country.
#
# Table: Weather
#
# +---------------+------+
# | Column Name   | Type |
# +---------------+------+
# | country_id    | int  |
# | weather_state | int  |
# | day           | date |
# +---------------+------+
# (country_id, day) is the primary key (combination of columns with unique
# values) for this table.
# Each row of this table indicates the weather state in a country for one
# day.
#
# Write a solution to find the type of weather in each country for
# November 2019.
#
# The type of weather is:
#
# Cold if the average weather_state is less than or equal 15,
#
# Hot if the average weather_state is greater than or equal to 25, and
#
# Warm otherwise.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Countries table:
# +------------+--------------+
# | country_id | country_name |
# +------------+--------------+
# | 2          | USA          |
# | 3          | Australia    |
# | 7          | Peru         |
# | 5          | China        |
# | 8          | Morocco      |
# | 9          | Spain        |
# +------------+--------------+
# Weather table:
# +------------+---------------+------------+
# | country_id | weather_state | day        |
# +------------+---------------+------------+
# | 2          | 15            | 2019-11-01 |
# | 2          | 12            | 2019-10-28 |
# | 2          | 12            | 2019-10-27 |
# | 3          | -2            | 2019-11-10 |
# | 3          | 0             | 2019-11-11 |
# | 3          | 3             | 2019-11-12 |
# | 5          | 16            | 2019-11-07 |
# | 5          | 18            | 2019-11-09 |
# | 5          | 21            | 2019-11-23 |
# | 7          | 25            | 2019-11-28 |
# | 7          | 22            | 2019-12-01 |
# | 7          | 20            | 2019-12-02 |
# | 8          | 25            | 2019-11-05 |
# | 8          | 27            | 2019-11-15 |
# | 8          | 31            | 2019-11-25 |
# | 9          | 7             | 2019-10-23 |
# | 9          | 3             | 2019-12-23 |
# +------------+---------------+------------+
# Output:
# +--------------+--------------+
# | country_name | weather_type |
# +--------------+--------------+
# | USA          | Cold         |
# | Australia    | Cold         |
# | Peru         | Hot          |
# | Morocco      | Hot          |
# | China        | Warm         |
# +--------------+--------------+
# Explanation:
# Average weather_state in USA in November is (15) / 1 = 15 so weather
# type is Cold.
# Average weather_state in Austraila in November is (-2 + 0 + 3) / 3 =
# 0.333 so weather type is Cold.
# Average weather_state in Peru in November is (25) / 1 = 25 so the
# weather type is Hot.
# Average weather_state in China in November is (16 + 18 + 21) / 3 =
# 18.333 so weather type is Warm.
# Average weather_state in Morocco in November is (25 + 27 + 31) / 3 =
# 27.667 so weather type is Hot.
# We know nothing about the average weather_state in Spain in November so
# we do not include it in the result table.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. For each country, average weather temperature in Nov 2019 and
        map to Cold/Hot/Warm. Join Countries to Weather on country_id; filter
        day in November 2019; AVG(weather_state).

        Algorithm:
        - JOIN Countries c JOIN Weather w ON country_id.
        - WHERE day BETWEEN '2019-11-01' AND '2019-11-30'.
        - GROUP BY country; CASE on AVG: <=15 Cold, >=25 Hot, else Warm.

        Complexity: O(W) scan of weather rows in range.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        c.country_name,
        CASE
            WHEN AVG(w.weather_state) <= 15 THEN 'Cold'
            WHEN AVG(w.weather_state) >= 25 THEN 'Hot'
            ELSE 'Warm'
        END AS weather_type
    FROM Countries c
    JOIN Weather w ON c.country_id = w.country_id
    WHERE w.day BETWEEN '2019-11-01' AND '2019-11-30'
    GROUP BY c.country_id, c.country_name;
    """
# @lc code=end
