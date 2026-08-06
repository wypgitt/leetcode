#
# @lc app=leetcode id=1194 lang=python3
#
# [1194] Tournament Winners
#
# https://leetcode.com/problems/tournament-winners/description/
#
# database
# Hard (50.14%)
# Likes:    152
# Dislikes: 57
# Total Accepted:    25.5K
# Total Submissions: 50.9K
# Testcase Example:  "{\"headers\":{\"Players\":[\"player_id\",\"group_id\"],\"Matches\":[\"match_id\",\"first_player\",\"second_player\",\"first_score\",\"second_score\"]},\"rows\":{\"Players\":[[10,2],[15,1],[20,3],[25,1],[30,1],[35,2],[40,3],[45,1],[50,2]],\"Matches\":[[1,15,45,3,0],[2,30,25,1,2],[3,30,15,2,0],[4,40,20,5,2],[5,35,50,1,1]]}}"
#
#
# Table: Players
#
# +-------------+-------+
# | Column Name | Type  |
# +-------------+-------+
# | player_id   | int   |
# | group_id    | int   |
# +-------------+-------+
# player_id is the primary key (column with unique values) of this table.
# Each row of this table indicates the group of each player.
#
# Table: Matches
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | match_id      | int     |
# | first_player  | int     |
# | second_player | int     |
# | first_score   | int     |
# | second_score  | int     |
# +---------------+---------+
# match_id is the primary key (column with unique values) of this table.
# Each row is a record of a match, first_player and second_player contain
# the player_id of each match.
# first_score and second_score contain the number of points of the
# first_player and second_player respectively.
# You may assume that, in each match, players belong to the same group.
#
# The winner in each group is the player who scored the maximum total
# points within the group. In the case of a tie, the lowest player_id
# wins.
#
# Write a solution to find the winner in each group.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Players table:
# +-----------+------------+
# | player_id | group_id   |
# +-----------+------------+
# | 15        | 1          |
# | 25        | 1          |
# | 30        | 1          |
# | 45        | 1          |
# | 10        | 2          |
# | 35        | 2          |
# | 50        | 2          |
# | 20        | 3          |
# | 40        | 3          |
# +-----------+------------+
# Matches table:
# +------------+--------------+---------------+-------------+--------------+
# | match_id   | first_player | second_player | first_score | second_score
# |
# +------------+--------------+---------------+-------------+--------------+
# | 1          | 15           | 45            | 3           | 0
# |
# | 2          | 30           | 25            | 1           | 2
# |
# | 3          | 30           | 15            | 2           | 0
# |
# | 4          | 40           | 20            | 5           | 2
# |
# | 5          | 35           | 50            | 1           | 1
# |
# +------------+--------------+---------------+-------------+--------------+
# Output:
# +-----------+------------+
# | group_id  | player_id  |
# +-----------+------------+
# | 1         | 15         |
# | 2         | 35         |
# | 3         | 40         |
# +-----------+------------+
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium: each player belongs to a group. Sum scores from matches
        (as first or second player). Per group, pick the player with highest
        total score; ties → lowest player_id.

        Algorithm:
        - UNION ALL scores for first/second player; SUM by player_id.
        - JOIN Players for group_id; RANK/ROW_NUMBER by score DESC, player_id ASC
          PARTITION BY group_id; filter rank=1.

        Complexity: O(N log N) with window sort.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    WITH scores AS (
        SELECT first_player AS player_id, first_score AS score FROM Matches
        UNION ALL
        SELECT second_player AS player_id, second_score AS score FROM Matches
    ),
    totals AS (
        SELECT p.group_id, p.player_id, IFNULL(SUM(s.score), 0) AS total_score
        FROM Players p
        LEFT JOIN scores s ON p.player_id = s.player_id
        GROUP BY p.group_id, p.player_id
    ),
    ranked AS (
        SELECT group_id, player_id,
               RANK() OVER (
                   PARTITION BY group_id
                   ORDER BY total_score DESC, player_id ASC
               ) AS rk
        FROM totals
    )
    SELECT group_id, player_id
    FROM ranked
    WHERE rk = 1;
    """
# @lc code=end
