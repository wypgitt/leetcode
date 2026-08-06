#
# @lc app=leetcode id=1341 lang=python3
#
# [1341] Movie Rating
#
# https://leetcode.com/problems/movie-rating/description/
#
# algorithms
# Medium (44.07%)
# Likes:    1042
# Dislikes: 244
# Total Accepted:    325K
# Total Submissions: 737K
# Testcase Example:  "{\"headers\": {\"Movies\": [\"movie_id\", \"title\"], \"Users\": [\"user_id\", \"name\"], \"MovieRating\": [\"movie_id\", \"user_id\", \"rating\", \"created_at\"]}, \"rows\": {\"Movies\": [[1, \"Avengers\"], [2, \"Frozen 2\"], [3, \"Joker\"]], \"Users\": [[1, \"Daniel\"], [2, \"Monica\"], [3, \"Maria\"], [4, \"James\"]], \"MovieRating\": [[1, 1, 3, \"2020-01-12\"], [1, 2, 4, \"2020-02-11\"], [1, 3, 2, \"2020-02-12\"], [1, 4, 1, \"2020-01-01\"], [2, 1, 5, \"2020-02-17\"], [2, 2, 2, \"2020-02-01\"], [2, 3, 2, \"2020-03-01\"], [3, 1, 3, \"2020-02-22\"], [3, 2, 4, \"2020-02-25\"]]}}"
#
# Table: Movies
#
# +---------------+---------+
# | Column Name | Type |
# +---------------+---------+
# | movie_id | int |
# | title | varchar |
# +---------------+---------+
# movie_id is the primary key (column with unique values) for this table.
# title is the name of the movie.
# Each movie has a unique title.
#
# Table: Users
#
# +---------------+---------+
# | Column Name | Type |
# +---------------+---------+
# | user_id | int |
# | name | varchar |
# +---------------+---------+
# user_id is the primary key (column with unique values) for this table.
# The column 'name' has unique values.
#
# Table: MovieRating
#
# +---------------+---------+
# | Column Name | Type |
# +---------------+---------+
# | movie_id | int |
# | user_id | int |
# | rating | int |
# | created_at | date |
# +---------------+---------+
# (movie_id, user_id) is the primary key (column with unique values) for this
# table.
# This table contains the rating of a movie by a user in their review.
# created_at is the user's review date.
#
# Write a solution to:
#
# Find the name of the user who has rated the greatest number of movies. In
# case of a tie, return the lexicographically smaller user name.
#
# Find the movie name with the highest average rating in February 2020. In case
# of a tie, return the lexicographically smaller movie name.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Movies table:
# +-------------+--------------+
# | movie_id | title |
# +-------------+--------------+
# | 1 | Avengers |
# | 2 | Frozen 2 |
# | 3 | Joker |
# +-------------+--------------+
# Users table:
# +-------------+--------------+
# | user_id | name |
# +-------------+--------------+
# | 1 | Daniel |
# | 2 | Monica |
# | 3 | Maria |
# | 4 | James |
# +-------------+--------------+
# MovieRating table:
# +-------------+--------------+--------------+-------------+
# | movie_id | user_id | rating | created_at |
# +-------------+--------------+--------------+-------------+
# | 1 | 1 | 3 | 2020-01-12 |
# | 1 | 2 | 4 | 2020-02-11 |
# | 1 | 3 | 2 | 2020-02-12 |
# | 1 | 4 | 1 | 2020-01-01 |
# | 2 | 1 | 5 | 2020-02-17 |
# | 2 | 2 | 2 | 2020-02-01 |
# | 2 | 3 | 2 | 2020-03-01 |
# | 3 | 1 | 3 | 2020-02-22 |
# | 3 | 2 | 4 | 2020-02-25 |
# +-------------+--------------+--------------+-------------+
# Output:
# +--------------+
# | results |
# +--------------+
# | Daniel |
# | Frozen 2 |
# +--------------+
# Explanation:
# Daniel and Monica have rated 3 movies ("Avengers", "Frozen 2" and "Joker")
# but Daniel is smaller lexicographically.
# Frozen 2 and Joker have a rating average of 3.5 in February but Frozen 2 is
# smaller lexicographically.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Find (1) user who rated the most movies (tie: lex smaller name);
        (2) movie with highest avg rating in Feb 2020 (tie: lex smaller title).
        Return as one-column results via UNION ALL.

        Algorithm:
        - Top user by COUNT ratings ORDER BY cnt DESC, name ASC LIMIT 1.
        - Top movie by AVG in Feb 2020 ORDER BY avg DESC, title ASC LIMIT 1.
        - UNION ALL into results.

        Complexity: O(R log R) with sorts / aggregation.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    (
        SELECT u.name AS results
        FROM Users u
        JOIN MovieRating mr ON u.user_id = mr.user_id
        GROUP BY u.user_id, u.name
        ORDER BY COUNT(*) DESC, u.name ASC
        LIMIT 1
    )
    UNION ALL
    (
        SELECT m.title AS results
        FROM Movies m
        JOIN MovieRating mr ON m.movie_id = mr.movie_id
        WHERE mr.created_at >= '2020-02-01' AND mr.created_at < '2020-03-01'
        GROUP BY m.movie_id, m.title
        ORDER BY AVG(mr.rating) DESC, m.title ASC
        LIMIT 1
    );
    """
# @lc code=end

