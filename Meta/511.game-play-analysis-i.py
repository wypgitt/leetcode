#
# @lc app=leetcode id=511 lang=python3
#
# [511] Game Play Analysis I
#
# https://leetcode.com/problems/game-play-analysis-i/description/
#
# algorithms
# Easy (76.56%)
# Likes:    1121
# Dislikes: 48
# Total Accepted:    583K
# Total Submissions: 762K
# Testcase Example:  "{\"headers\":{\"Activity\":[\"player_id\",\"device_id\",\"event_date\",\"games_played\"]},\"rows\":{\"Activity\":[[1,2,\"2016-03-01\",5],[1,2,\"2016-05-02\",6],[2,3,\"2017-06-25\",1],[3,1,\"2016-03-02\",0],[3,4,\"2018-07-03\",5]]}}"
#
# Table: Activity
#
# +--------------+---------+
# | Column Name | Type |
# +--------------+---------+
# | player_id | int |
# | device_id | int |
# | event_date | date |
# | games_played | int |
# +--------------+---------+
# (player_id, event_date) is the primary key (combination of columns with
# unique values) of this table.
# This table shows the activity of players of some games.
# Each row is a record of a player who logged in and played a number of games
# (possibly 0) before logging out on someday using some device.
#
# Write a solution to find the first login date for each player.
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
# | 1 | 2 | 2016-03-01 | 5 |
# | 1 | 2 | 2016-05-02 | 6 |
# | 2 | 3 | 2017-06-25 | 1 |
# | 3 | 1 | 2016-03-02 | 0 |
# | 3 | 4 | 2018-07-03 | 5 |
# +-----------+-----------+------------+--------------+
# Output:
# +-----------+-------------+
# | player_id | first_login |
# +-----------+-------------+
# | 1 | 2016-03-01 |
# | 2 | 2017-06-25 |
# | 3 | 2016-03-02 |
# +-----------+-------------+
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        First login per player is the earliest event_date for that player_id.

        Algorithm:
        - GROUP BY player_id and take MIN(event_date) as first_login.

        Complexity: O(n) scan with hash aggregate (or sort+group).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        player_id,
        MIN(event_date) AS first_login
    FROM Activity
    GROUP BY player_id;
    """
# @lc code=end
