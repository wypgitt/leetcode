#
# @lc app=leetcode id=1811 lang=python3
#
# [1811] Find Interview Candidates
#
# https://leetcode.com/problems/find-interview-candidates/description/
#
# database
# Medium (60.74%)
# Likes:    212
# Dislikes: 30
# Total Accepted:    20K
# Total Submissions: 32.9K
# Testcase Example:  "{\"headers\":{\"Contests\":[\"contest_id\",\"gold_medal\",\"silver_medal\",\"bronze_medal\"],\"Users\":[\"user_id\",\"mail\",\"name\"]},\"rows\":{\"Contests\":[[190,1,5,2],[191,2,3,5],[192,5,2,3],[193,1,3,5],[194,4,5,2],[195,4,2,1],[196,1,5,2]],\"Users\":[[1,\"sarah@leetcode.com\",\"Sarah\"],[2,\"bob@leetcode.com\",\"Bob\"],[3,\"alice@leetcode.com\",\"Alice\"],[4,\"hercy@leetcode.com\",\"Hercy\"],[5,\"quarz@leetcode.com\",\"Quarz\"]]}}"
#
#
# Table: Contests
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | contest_id   | int  |
# | gold_medal   | int  |
# | silver_medal | int  |
# | bronze_medal | int  |
# +--------------+------+
# contest_id is the column with unique values for this table.
# This table contains the LeetCode contest ID and the user IDs of the
# gold, silver, and bronze medalists.
# It is guaranteed that any consecutive contests have consecutive IDs and
# that no ID is skipped.
#
# Table: Users
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | user_id     | int     |
# | mail        | varchar |
# | name        | varchar |
# +-------------+---------+
# user_id is the column with unique values for this table.
# This table contains information about the users.
#
# Write a solution to report the name and the mail of all interview
# candidates. A user is an interview candidate if at least one of these
# two conditions is true:
#
# The user won any medal in three or more consecutive contests.
#
# The user won the gold medal in three or more different contests (not
# necessarily consecutive).
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Contests table:
# +------------+------------+--------------+--------------+
# | contest_id | gold_medal | silver_medal | bronze_medal |
# +------------+------------+--------------+--------------+
# | 190        | 1          | 5            | 2            |
# | 191        | 2          | 3            | 5            |
# | 192        | 5          | 2            | 3            |
# | 193        | 1          | 3            | 5            |
# | 194        | 4          | 5            | 2            |
# | 195        | 4          | 2            | 1            |
# | 196        | 1          | 5            | 2            |
# +------------+------------+--------------+--------------+
# Users table:
# +---------+--------------------+-------+
# | user_id | mail               | name  |
# +---------+--------------------+-------+
# | 1       | sarah@leetcode.com | Sarah |
# | 2       | bob@leetcode.com   | Bob   |
# | 3       | alice@leetcode.com | Alice |
# | 4       | hercy@leetcode.com | Hercy |
# | 5       | quarz@leetcode.com | Quarz |
# +---------+--------------------+-------+
# Output:
# +-------+--------------------+
# | name  | mail               |
# +-------+--------------------+
# | Sarah | sarah@leetcode.com |
# | Bob   | bob@leetcode.com   |
# | Alice | alice@leetcode.com |
# | Quarz | quarz@leetcode.com |
# +-------+--------------------+
# Explanation:
# Sarah won 3 gold medals (190, 193, and 196), so we include her in the
# result table.
# Bob won a medal in 3 consecutive contests (190, 191, and 192), so we
# include him in the result table.
#     - Note that he also won a medal in 3 other consecutive contests
# (194, 195, and 196).
# Alice won a medal in 3 consecutive contests (191, 192, and 193), so we
# include her in the result table.
# Quarz won a medal in 5 consecutive contests (190, 191, 192, 193, and
# 194), so we include them in the result table.
#
# Follow up:
#
# What if the first condition changed to be "any medal in n or more
# consecutive contests"? How would you change your solution to get the
# interview candidates? Imagine that n is the parameter of a stored
# procedure.
#
# Some users may not participate in every contest but still perform well
# in the ones they do. How would you change your solution to only consider
# contests where the user was a participant? Suppose the registered users
# for each contest are given in another table.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Interview candidates: users with >=3 gold medals OR medals
        in 3 consecutive contests. Return name, mail ordered by name/mail.

        Algorithm:
        - Unpivot contest medals; count golds; window consecutive contest streaks
          of any medal; UNION criteria; join Users.

        Complexity: O(C + U) with grouping.
        """
        return self.sql

    sql = """
    WITH medals AS (
      SELECT contest_id, gold_medal AS user_id, 'gold' AS medal FROM Contests
      UNION ALL
      SELECT contest_id, silver_medal, 'silver' FROM Contests
      UNION ALL
      SELECT contest_id, bronze_medal, 'bronze' FROM Contests
    ),
    golds AS (
      SELECT user_id
      FROM medals
      WHERE medal = 'gold'
      GROUP BY user_id
      HAVING COUNT(*) >= 3
    ),
    ranked AS (
      SELECT user_id, contest_id,
             contest_id - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY contest_id) AS grp
      FROM (SELECT DISTINCT user_id, contest_id FROM medals) t
    ),
    consecutive AS (
      SELECT user_id
      FROM ranked
      GROUP BY user_id, grp
      HAVING COUNT(*) >= 3
    ),
    cand AS (
      SELECT user_id FROM golds
      UNION
      SELECT user_id FROM consecutive
    )
    SELECT u.name, u.mail
    FROM Users u
    JOIN cand c ON u.user_id = c.user_id
    ORDER BY u.name, u.mail;
    """
# @lc code=end
