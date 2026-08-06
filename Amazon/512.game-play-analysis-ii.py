#
# @lc app=leetcode id=512 lang=python3
#
# [512] Game Play Analysis II
#
# https://leetcode.com/problems/game-play-analysis-ii/description/
#
# database
# Easy (54.82%)
# Likes:    279
# Dislikes: 43
# Total Accepted:    109.5K
# Total Submissions: 199.7K
# Testcase Example:  "{\"headers\":{\"Activity\":[\"player_id\",\"device_id\",\"event_date\",\"games_played\"]},\"rows\":{\"Activity\":[[1,2,\"2016-03-01\",5],[1,2,\"2016-05-02\",6],[2,3,\"2017-06-25\",1],[3,1,\"2016-03-02\",0],[3,4,\"2018-07-03\",5]]}}"
#
#
# Table: Activity
#
# +--------------+---------+
# | Column Name  | Type    |
# +--------------+---------+
# | player_id    | int     |
# | device_id    | int     |
# | event_date   | date    |
# | games_played | int     |
# +--------------+---------+
# (player_id, event_date) is the primary key (combination of columns with
# unique values) of this table.
# This table shows the activity of players of some games.
# Each row is a record of a player who logged in and played a number of
# games (possibly 0) before logging out on someday using some device.
#
# Write a solution to report the device that is first logged in for each
# player.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Activity table:
# +-----------+-----------+------------+--------------+
# | player_id | device_id | event_date | games_played |
# +-----------+-----------+------------+--------------+
# | 1         | 2         | 2016-03-01 | 5            |
# | 1         | 2         | 2016-05-02 | 6            |
# | 2         | 3         | 2017-06-25 | 1            |
# | 3         | 1         | 2016-03-02 | 0            |
# | 3         | 4         | 2018-07-03 | 5            |
# +-----------+-----------+------------+--------------+
# Output:
# +-----------+-----------+
# | player_id | device_id |
# +-----------+-----------+
# | 1         | 2         |
# | 2         | 3         |
# | 3         | 1         |
# +-----------+-----------+
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        For each player, return the device_id used on their first login date.

        Algorithm:
        - Find MIN(event_date) per player (subquery / JOIN).
        - Join back to Activity on (player_id, event_date) to get device_id.

        Complexity: O(n) with aggregation + join on primary key.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        a.player_id,
        a.device_id
    FROM Activity a
    JOIN (
        SELECT player_id, MIN(event_date) AS first_login
        FROM Activity
        GROUP BY player_id
    ) t
      ON a.player_id = t.player_id
     AND a.event_date = t.first_login;
    """
# @lc code=end
