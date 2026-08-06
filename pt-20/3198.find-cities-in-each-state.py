#
# @lc app=leetcode id=3198 lang=python3
#
# [3198] Find Cities in Each State
#
# https://leetcode.com/problems/find-cities-in-each-state/description/
#
# database
# Easy (79.20%)
# Likes:    9
# Dislikes: 2
# Total Accepted:    4.1K
# Total Submissions: 5.2K
# Testcase Example:  "{\"headers\":{\"cities\":[\"state\",\"city\"]},\"rows\":{\"cities\":[[\"California\",\"Los Angeles\"],[\"California\",\"San Francisco\"],[\"California\",\"San Diego\"],[\"Texas\",\"Houston\"],[\"Texas\",\"Austin\"],[\"Texas\",\"Dallas\"],[\"New York\",\"New York City\"],[\"New York\",\"Buffalo\"],[\"New York\",\"Rochester\"]]}}"
#
#
# Table: cities
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | state       | varchar |
# | city        | varchar |
# +-------------+---------+
# (state, city) is the primary key (combination of columns with unique
# values) for this table.
# Each row of this table contains the state name and the city name within
# that state.
#
# Write a solution to find all the cities in each state and combine them
# into a single comma-separated string.
#
# Return the result table ordered by state and city in ascending order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# cities table:
#
# +-------------+---------------+
# | state       | city          |
# +-------------+---------------+
# | California  | Los Angeles   |
# | California  | San Francisco |
# | California  | San Diego     |
# | Texas       | Houston       |
# | Texas       | Austin        |
# | Texas       | Dallas        |
# | New York    | New York City |
# | New York    | Buffalo       |
# | New York    | Rochester     |
# +-------------+---------------+
#
# Output:
#
# +-------------+---------------------------------------+
# | state       | cities                                |
# +-------------+---------------------------------------+
# | California  | Los Angeles, San Diego, San Francisco |
# | New York    | Buffalo, New York City, Rochester     |
# | Texas       | Austin, Dallas, Houston               |
# +-------------+---------------------------------------+
#
# Explanation:
#
# California: All cities ("Los Angeles", "San Diego", "San Francisco") are
# listed in a comma-separated string.
#
# New York: All cities ("Buffalo", "New York City", "Rochester") are
# listed in a comma-separated string.
#
# Texas: All cities ("Austin", "Dallas", "Houston") are listed in a
# comma-separated string.
#
# Note: The output table is ordered by the state name in ascending order.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: cities(state, city). For each state, comma-separate cities
        sorted ascending; order rows by state.

        Algorithm:
        - GROUP BY state; GROUP_CONCAT(city ORDER BY city SEPARATOR ', ').

        Complexity: O(N log N) within groups for ordering.
        """
        self.sql = """
SELECT
    state,
    GROUP_CONCAT(city ORDER BY city SEPARATOR ', ') AS cities
FROM cities
GROUP BY 1
ORDER BY 1;
"""
        return self.sql
# @lc code=end
