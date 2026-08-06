#
# @lc app=leetcode id=2314 lang=python3
#
# [2314] The First Day of the Maximum Recorded Degree in Each City
#
# https://leetcode.com/problems/the-first-day-of-the-maximum-recorded-degree-in-each-city/description/
#
# database
# Medium (73.56%)
# Likes:    58
# Dislikes: 2
# Total Accepted:    8.7K
# Total Submissions: 11.8K
# Testcase Example:  "{\"headers\": {\"Weather\": [\"city_id\", \"day\", \"degree\"]}, \"rows\": {\"Weather\": [[1, \"2022-01-07\", -12], [1, \"2022-03-07\", 5], [1, \"2022-07-07\", 24], [2, \"2022-08-07\", 37], [2, \"2022-08-17\", 37], [3, \"2022-02-07\", -7], [3, \"2022-12-07\", -6]]}}"
#
#
# Table: Weather
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | city_id     | int  |
# | day         | date |
# | degree      | int  |
# +-------------+------+
# (city_id, day) is the primary key (combination of columns with unique
# values) for this table.
# Each row in this table contains the degree of the weather of a city on a
# certain day.
# All the degrees are recorded in the year 2022.
#
# Write a solution to report the day that has the maximum recorded degree
# in each city. If the maximum degree was recorded for the same city
# multiple times, return the earliest day among them.
#
# Return the result table ordered by city_id in ascending order.
#
# The result format is shown in the following example.
#
# Example 1:
#
# Input:
# Weather table:
# +---------+------------+--------+
# | city_id | day        | degree |
# +---------+------------+--------+
# | 1       | 2022-01-07 | -12    |
# | 1       | 2022-03-07 | 5      |
# | 1       | 2022-07-07 | 24     |
# | 2       | 2022-08-07 | 37     |
# | 2       | 2022-08-17 | 37     |
# | 3       | 2022-02-07 | -7     |
# | 3       | 2022-12-07 | -6     |
# +---------+------------+--------+
# Output:
# +---------+------------+--------+
# | city_id | day        | degree |
# +---------+------------+--------+
# | 1       | 2022-07-07 | 24     |
# | 2       | 2022-08-07 | 37     |
# | 3       | 2022-12-07 | -6     |
# +---------+------------+--------+
# Explanation:
# For city 1, the maximum degree was recorded on 2022-07-07 with 24
# degrees.
# For city 2, the maximum degree was recorded on 2022-08-07 and 2022-08-17
# with 37 degrees. We choose the earlier date (2022-08-07).
# For city 3, the maximum degree was recorded on 2022-12-07 with -6
# degrees.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL: Weather(city_id, day, degree). For each city, the day of its
        maximum degree (earliest day on ties). Order by city_id.

        Algorithm:
        - RANK() PARTITION BY city_id ORDER BY degree DESC, day; keep rk=1.

        Complexity: O(N log N).
        """
        self.sql = """
WITH T AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY city_id
            ORDER BY degree DESC, day
        ) AS rk
    FROM Weather
)
SELECT city_id, day, degree
FROM T
WHERE rk = 1
ORDER BY city_id;
"""
        return self.sql
# @lc code=end
