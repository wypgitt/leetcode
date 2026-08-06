#
# @lc app=leetcode id=1308 lang=python3
#
# [1308] Running Total for Different Genders
#
# https://leetcode.com/problems/running-total-for-different-genders/description/
#
# database
# Medium (86.05%)
# Likes:    225
# Dislikes: 70
# Total Accepted:    48K
# Total Submissions: 55.7K
# Testcase Example:  "{\"headers\":{\"Scores\":[\"player_name\",\"gender\",\"day\",\"score_points\"]},\"rows\":{\"Scores\":[[\"Aron\",\"F\",\"2020-01-01\",17],[\"Alice\",\"F\",\"2020-01-07\",23],[\"Bajrang\",\"M\",\"2020-01-07\",7],[\"Khali\",\"M\",\"2019-12-25\",11],[\"Slaman\",\"M\",\"2019-12-30\",13],[\"Joe\",\"M\",\"2019-12-31\",3],[\"Jose\",\"M\",\"2019-12-18\",2],[\"Priya\",\"F\",\"2019-12-31\",23],[\"Priyanka\",\"F\",\"2019-12-30\",17]]}}"
#
#
# Table: Scores
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | player_name   | varchar |
# | gender        | varchar |
# | day           | date    |
# | score_points  | int     |
# +---------------+---------+
# (gender, day) is the primary key (combination of columns with unique
# values) for this table.
# A competition is held between the female team and the male team.
# Each row of this table indicates that a player_name and with gender has
# scored score_point in someday.
# Gender is 'F' if the player is in the female team and 'M' if the player
# is in the male team.
#
# Write a solution to find the total score for each gender on each day.
#
# Return the result table ordered by gender and day in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Scores table:
# +-------------+--------+------------+--------------+
# | player_name | gender | day        | score_points |
# +-------------+--------+------------+--------------+
# | Aron        | F      | 2020-01-01 | 17           |
# | Alice       | F      | 2020-01-07 | 23           |
# | Bajrang     | M      | 2020-01-07 | 7            |
# | Khali       | M      | 2019-12-25 | 11           |
# | Slaman      | M      | 2019-12-30 | 13           |
# | Joe         | M      | 2019-12-31 | 3            |
# | Jose        | M      | 2019-12-18 | 2            |
# | Priya       | F      | 2019-12-31 | 23           |
# | Priyanka    | F      | 2019-12-30 | 17           |
# +-------------+--------+------------+--------------+
# Output:
# +--------+------------+-------+
# | gender | day        | total |
# +--------+------------+-------+
# | F      | 2019-12-30 | 17    |
# | F      | 2019-12-31 | 40    |
# | F      | 2020-01-01 | 57    |
# | F      | 2020-01-07 | 80    |
# | M      | 2019-12-18 | 2     |
# | M      | 2019-12-25 | 13    |
# | M      | 2019-12-30 | 26    |
# | M      | 2019-12-31 | 29    |
# | M      | 2020-01-07 | 36    |
# +--------+------------+-------+
# Explanation:
# For the female team:
# The first day is 2019-12-30, Priyanka scored 17 points and the total
# score for the team is 17.
# The second day is 2019-12-31, Priya scored 23 points and the total score
# for the team is 40.
# The third day is 2020-01-01, Aron scored 17 points and the total score
# for the team is 57.
# The fourth day is 2020-01-07, Alice scored 23 points and the total score
# for the team is 80.
#
# For the male team:
# The first day is 2019-12-18, Jose scored 2 points and the total score
# for the team is 2.
# The second day is 2019-12-25, Khali scored 11 points and the total score
# for the team is 13.
# The third day is 2019-12-30, Slaman scored 13 points and the total score
# for the team is 26.
# The fourth day is 2019-12-31, Joe scored 3 points and the total score
# for the team is 29.
# The fifth day is 2020-01-07, Bajrang scored 7 points and the total score
# for the team is 36.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Scores(player_name, gender, day, score_points). For each
        gender compute running total of score_points ordered by day.

        Algorithm:
        - SUM(score_points) OVER (PARTITION BY gender ORDER BY day) AS total.

        Complexity: O(N log N) with window ordering.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        gender,
        day,
        SUM(score_points) OVER (
            PARTITION BY gender
            ORDER BY day
        ) AS total
    FROM Scores
    ORDER BY gender, day;
    """
# @lc code=end

