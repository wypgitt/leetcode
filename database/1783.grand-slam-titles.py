#
# @lc app=leetcode id=1783 lang=python3
#
# [1783] Grand Slam Titles
#
# https://leetcode.com/problems/grand-slam-titles/description/
#
# database
# Medium (82.97%)
# Likes:    246
# Dislikes: 10
# Total Accepted:    35.1K
# Total Submissions: 42.3K
# Testcase Example:  "{\"headers\": {\"Players\": [\"player_id\", \"player_name\"], \"Championships\": [\"year\", \"Wimbledon\", \"Fr_open\", \"US_open\", \"Au_open\"]}, \"rows\": {\"Players\": [[1, \"Nadal\"], [2, \"Federer\"], [3, \"Novak\"]], \"Championships\": [[2018, 1, 1, 1, 1], [2019, 1, 1, 2, 2], [2020, 2, 1, 2, 2]]}}"
#
#
# Table: Players
#
# +----------------+---------+
# | Column Name    | Type    |
# +----------------+---------+
# | player_id      | int     |
# | player_name    | varchar |
# +----------------+---------+
# player_id is the primary key (column with unique values) for this table.
# Each row in this table contains the name and the ID of a tennis player.
#
# Table: Championships
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | year          | int     |
# | Wimbledon     | int     |
# | Fr_open       | int     |
# | US_open       | int     |
# | Au_open       | int     |
# +---------------+---------+
# year is the primary key (column with unique values) for this table.
# Each row of this table contains the IDs of the players who won one each
# tennis tournament of the grand slam.
#
# Write a solution to report the number of grand slam tournaments won by
# each player. Do not include the players who did not win any tournament.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Players table:
# +-----------+-------------+
# | player_id | player_name |
# +-----------+-------------+
# | 1         | Nadal       |
# | 2         | Federer     |
# | 3         | Novak       |
# +-----------+-------------+
# Championships table:
# +------+-----------+---------+---------+---------+
# | year | Wimbledon | Fr_open | US_open | Au_open |
# +------+-----------+---------+---------+---------+
# | 2018 | 1         | 1       | 1       | 1       |
# | 2019 | 1         | 1       | 2       | 2       |
# | 2020 | 2         | 1       | 2       | 2       |
# +------+-----------+---------+---------+---------+
# Output:
# +-----------+-------------+-------------------+
# | player_id | player_name | grand_slams_count |
# +-----------+-------------+-------------------+
# | 2         | Federer     | 5                 |
# | 1         | Nadal       | 7                 |
# +-----------+-------------+-------------------+
# Explanation:
# Player 1 (Nadal) won 7 titles: Wimbledon (2018, 2019), Fr_open (2018,
# 2019, 2020), US_open (2018), and Au_open (2018).
# Player 2 (Federer) won 5 titles: Wimbledon (2020), US_open (2019, 2020),
# and Au_open (2019, 2020).
# Player 3 (Novak) did not win anything, we did not include them in the
# result table.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Championships has year + Wimbledon/Fr_open/US_open/Au_open
        player ids. Players has player_id, player_name. Count grand-slam titles
        per player (each column win = 1 title).

        Algorithm:
        - UNION ALL the four slam columns into (player_id); GROUP BY count;
          JOIN Players for names; only players with ≥1 title.

        Complexity: O(C) scan of championships.
        """
        return self.sql

    sql = """
    SELECT p.player_id, p.player_name, COUNT(*) AS grand_slams_count
    FROM (
        SELECT Wimbledon AS player_id FROM Championships
        UNION ALL
        SELECT Fr_open FROM Championships
        UNION ALL
        SELECT US_open FROM Championships
        UNION ALL
        SELECT Au_open FROM Championships
    ) t
    JOIN Players p ON p.player_id = t.player_id
    GROUP BY p.player_id, p.player_name;
    """
# @lc code=end
