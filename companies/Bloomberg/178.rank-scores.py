#
# @lc app=leetcode id=178 lang=python3
#
# [178] Rank Scores
#
# https://leetcode.com/problems/rank-scores/description/
#
# algorithms
# Medium (68.43%)
# Likes:    2534
# Dislikes: 304
# Total Accepted:    748K
# Total Submissions: 1.1M
# Testcase Example:  "{\"headers\": {\"Scores\": [\"id\", \"score\"]}, \"rows\": {\"Scores\": [[1, 3.50], [2, 3.65], [3, 4.00], [4, 3.85], [5, 4.00], [6, 3.65]]}}"
#
# Table: Scores
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | id | int |
# | score | decimal |
# +-------------+---------+
# id is the primary key (column with unique values) for this table.
# Each row of this table contains the score of a game. Score is a floating
# point value with two decimal places.
#
# Write a solution to find the rank of the scores. The ranking should be
# calculated according to the following rules:
#
# The scores should be ranked from the highest to the lowest.
#
# If there is a tie between two scores, both should have the same ranking.
#
# After a tie, the next ranking number should be the next consecutive integer
# value. In other words, there should be no holes between ranks.
#
# Return the result table ordered by score in descending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Scores table:
# +----+-------+
# | id | score |
# +----+-------+
# | 1 | 3.50 |
# | 2 | 3.65 |
# | 3 | 4.00 |
# | 4 | 3.85 |
# | 5 | 4.00 |
# | 6 | 3.65 |
# +----+-------+
# Output:
# +-------+------+
# | score | rank |
# +-------+------+
# | 4.00 | 1 |
# | 4.00 | 1 |
# | 3.85 | 2 |
# | 3.65 | 3 |
# | 3.65 | 3 |
# | 3.50 | 4 |
# +-------+------+
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Ties share a rank and the next rank has no gaps — that is exactly
        DENSE_RANK (not RANK, which leaves holes after ties).

        Algorithm:
        - SELECT score, DENSE_RANK() OVER (ORDER BY score DESC) AS rank.
        - ORDER BY score DESC for the result presentation.

        Complexity: O(n log n) for the window sort over Scores; O(n) space
        for the ranking output.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        score,
        DENSE_RANK() OVER (ORDER BY score DESC) AS `rank`
    FROM Scores
    ORDER BY score DESC;
    """
# @lc code=end
