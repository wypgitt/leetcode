#
# @lc app=leetcode id=2991 lang=python3
#
# [2991] Top Three Wineries 
#
# https://leetcode.com/problems/top-three-wineries/description/
#
# database
# Hard (54.00%)
# Likes:    14
# Dislikes: 8
# Total Accepted:    3.9K
# Total Submissions: 7.2K
# Testcase Example:  "{\"headers\":{\"Wineries\":[\"id\",\"country\",\"points\",\"winery\"]},\"rows\":{\"Wineries\":[[103,\"Australia\",84,\"WhisperingPines\"],[737,\"Australia\",85,\"GrapesGalore\"],[848,\"Australia\",100,\"HarmonyHill\"],[222,\"Hungary\",60,\"MoonlitCellars\"],[116,\"USA\",47,\"RoyalVines\"],[124,\"USA\",45,\"Eagle'sNest\"],[648,\"India\",69,\"SunsetVines\"],[894,\"USA\",39,\"RoyalVines\"],[677,\"USA\",9,\"PacificCrest\"]]}}"
#
#
# Table: Wineries
#
# +-------------+----------+
# | Column Name | Type     |
# +-------------+----------+
# | id          | int      |
# | country     | varchar  |
# | points      | int      |
# | winery      | varchar  |
# +-------------+----------+
# id is column of unique values for this table.
# This table contains id, country, points, and winery.
#
# Write a solution to find the top three wineries in each country based on
# their total points. If multiple wineries have the same total points,
# order them by winery name in ascending order. If there's no second
# winery, output 'No second winery,' and if there's no third winery,
# output 'No third winery.'
#
# Return the result table ordered by country in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Wineries table:
# +-----+-----------+--------+-----------------+
# | id  | country   | points | winery          |
# +-----+-----------+--------+-----------------+
# | 103 | Australia | 84     | WhisperingPines |
# | 737 | Australia | 85     | GrapesGalore    |
# | 848 | Australia | 100    | HarmonyHill     |
# | 222 | Hungary   | 60     | MoonlitCellars  |
# | 116 | USA       | 47     | RoyalVines      |
# | 124 | USA       | 45     | Eagle'sNest     |
# | 648 | India     | 69     | SunsetVines     |
# | 894 | USA       | 39     | RoyalVines      |
# | 677 | USA       | 9      | PacificCrest    |
# +-----+-----------+--------+-----------------+
# Output:
# +-----------+---------------------+-------------------+----------------------+
# | country   | top_winery          | second_winery     | third_winery
# |
# +-----------+---------------------+-------------------+----------------------+
# | Australia | HarmonyHill (100)   | GrapesGalore (85) | WhisperingPines
# (84) |
# | Hungary   | MoonlitCellars (60) | No second winery  | No third winery
# |
# | India     | SunsetVines (69)    | No second winery  | No third winery
# |
# | USA       | RoyalVines (86)     | Eagle'sNest (45)  | PacificCrest (9)
# |
# +-----------+---------------------+-------------------+----------------------+
# Explanation
# For Australia
#  - HarmonyHill Winery accumulates the highest score of 100 points in
# Australia.
#  - GrapesGalore Winery has a total of 85 points, securing the
# second-highest position in Australia.
#  - WhisperingPines Winery has a total of 80 points, ranking as the
# third-highest.
# For Hungary
#  - MoonlitCellars is the sole winery, accruing 60 points, automatically
# making it the highest. There is no second or third winery.
# For India
#  - SunsetVines is the sole winery, earning 69 points, making it the top
# winery. There is no second or third winery.
# For the USA
#  - RoyalVines Wines accumulates a total of 47 + 39 = 86 points, claiming
# the highest position in the USA.
#  - Eagle'sNest has a total of 45 points, securing the second-highest
# position in the USA.
#  - PacificCrest accumulates 9 points, ranking as the third-highest
# winery in the USA
# Output table is ordered by country in ascending order.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Wineries(id, country, points, winery). Per country, top 3
        wineries by SUM(points) (tie-break winery ASC). Format "Name (points)".
        Missing 2nd/3rd => 'No second winery' / 'No third winery'. Order country.

        Algorithm:
        - Aggregate by (country, winery); RANK() by points DESC, winery ASC;
          self-join ranks 1/2/3 with IFNULL placeholders.

        Complexity: O(N log N).
        """
        self.sql = """
WITH
    T AS (
        SELECT
            country,
            CONCAT(winery, ' (', points, ')') AS winery,
            RANK() OVER (
                PARTITION BY country
                ORDER BY points DESC, winery
            ) AS rk
        FROM (
            SELECT country, SUM(points) AS points, winery
            FROM Wineries
            GROUP BY 1, 3
        ) AS t
    )
SELECT
    t1.country,
    t1.winery AS top_winery,
    IFNULL(t2.winery, 'No second winery') AS second_winery,
    IFNULL(t3.winery, 'No third winery') AS third_winery
FROM
    T AS t1
    LEFT JOIN T AS t2 ON t1.country = t2.country AND t1.rk = t2.rk - 1
    LEFT JOIN T AS t3 ON t2.country = t3.country AND t2.rk = t3.rk - 1
WHERE t1.rk = 1
ORDER BY 1;
"""
        return self.sql
# @lc code=end
