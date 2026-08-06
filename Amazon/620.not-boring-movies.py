#
# @lc app=leetcode id=620 lang=python3
#
# [620] Not Boring Movies
#
# https://leetcode.com/problems/not-boring-movies/description/
#
# algorithms
# Easy (75.16%)
# Likes:    1578
# Dislikes: 566
# Total Accepted:    1.2M
# Total Submissions: 1.6M
# Testcase Example:  "{\"headers\":{\"cinema\":[\"id\", \"movie\", \"description\", \"rating\"]},\"rows\":{\"cinema\":[[1, \"War\", \"great 3D\", 8.9], [2, \"Science\", \"fiction\", 8.5], [3, \"irish\", \"boring\", 6.2], [4, \"Ice song\", \"Fantacy\", 8.6], [5, \"House card\", \"Interesting\", 9.1]]}}"
#
# Table: Cinema
#
# +----------------+----------+
# | Column Name | Type |
# +----------------+----------+
# | id | int |
# | movie | varchar |
# | description | varchar |
# | rating | float |
# +----------------+----------+
# id is the primary key (column with unique values) for this table.
# Each row contains information about the name of a movie, its genre, and its
# rating.
# rating is a 2 decimal places float in the range [0, 10]
#
# Write a solution to report the movies with an odd-numbered ID and a
# description that is not "boring".
#
# Return the result table ordered by rating in descending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Cinema table:
# +----+------------+-------------+--------+
# | id | movie | description | rating |
# +----+------------+-------------+--------+
# | 1 | War | great 3D | 8.9 |
# | 2 | Science | fiction | 8.5 |
# | 3 | irish | boring | 6.2 |
# | 4 | Ice song | Fantacy | 8.6 |
# | 5 | House card | Interesting | 9.1 |
# +----+------------+-------------+--------+
# Output:
# +----+------------+-------------+--------+
# | id | movie | description | rating |
# +----+------------+-------------+--------+
# | 5 | House card | Interesting | 9.1 |
# | 1 | War | great 3D | 8.9 |
# +----+------------+-------------+--------+
# Explanation:
# We have three movies with odd-numbered IDs: 1, 3, and 5. The movie with ID =
# 3 is boring so we do not include it in the answer.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Odd-id movies that are not described as boring, ordered by rating descending.

        Algorithm:
        - WHERE id % 2 = 1 AND description != 'boring' ORDER BY rating DESC.

        Complexity: O(N log N) for sort.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT *
    FROM Cinema
    WHERE id % 2 = 1 AND description != 'boring'
    ORDER BY rating DESC;
    """
# @lc code=end
