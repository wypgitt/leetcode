#
# @lc app=leetcode id=2339 lang=python3
#
# [2339] All the Matches of the League
#
# https://leetcode.com/problems/all-the-matches-of-the-league/description/
#
# database
# Easy (88.38%)
# Likes:    49
# Dislikes: 4
# Total Accepted:    11.9K
# Total Submissions: 13.5K
# Testcase Example:  "{\"headers\": {\"Teams\": [\"team_name\"]}, \"rows\": {\"Teams\": [[\"Leetcode FC\"], [\"Ahly SC\"], [\"Real Madrid\"]]}}"
#
#
# Table: Teams
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | team_name   | varchar |
# +-------------+---------+
# team_name is the column with unique values of this table.
# Each row of this table shows the name of a team.
#
# Write a solution to report all the possible matches of the league. Note
# that every two teams play two matches with each other, with one team
# being the home_team once and the other time being the away_team.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Teams table:
# +-------------+
# | team_name   |
# +-------------+
# | Leetcode FC |
# | Ahly SC     |
# | Real Madrid |
# +-------------+
# Output:
# +-------------+-------------+
# | home_team   | away_team   |
# +-------------+-------------+
# | Real Madrid | Leetcode FC |
# | Real Madrid | Ahly SC     |
# | Leetcode FC | Real Madrid |
# | Leetcode FC | Ahly SC     |
# | Ahly SC     | Real Madrid |
# | Ahly SC     | Leetcode FC |
# +-------------+-------------+
# Explanation: All the matches of the league are shown in the table.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL: Teams(team_name). All ordered pairs of distinct teams as
        (home_team, away_team) — each pair plays home and away.

        Algorithm:
        - Self-join Teams where names differ.

        Complexity: O(N^2).
        """
        self.sql = """
SELECT t1.team_name AS home_team, t2.team_name AS away_team
FROM Teams AS t1
JOIN Teams AS t2
WHERE t1.team_name != t2.team_name;
"""
        return self.sql
# @lc code=end
