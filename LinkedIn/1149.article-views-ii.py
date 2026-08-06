#
# @lc app=leetcode id=1149 lang=python3
#
# [1149] Article Views II
#
# https://leetcode.com/problems/article-views-ii/description/
#
# database
# Medium (47.29%)
# Likes:    135
# Dislikes: 30
# Total Accepted:    45.3K
# Total Submissions: 95.7K
# Testcase Example:  "{\"headers\":{\"Views\":[\"article_id\",\"author_id\",\"viewer_id\",\"view_date\"]},\"rows\":{\"Views\":[[1,3,5,\"2019-08-01\"],[3,4,5,\"2019-08-01\"],[1,3,6,\"2019-08-02\"],[2,7,7,\"2019-08-01\"],[2,7,6,\"2019-08-02\"],[4,7,1,\"2019-07-22\"],[3,4,4,\"2019-07-21\"],[3,4,4,\"2019-07-21\"]]}}"
#
#
# Table: Views
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | article_id    | int     |
# | author_id     | int     |
# | viewer_id     | int     |
# | view_date     | date    |
# +---------------+---------+
# This table may have duplicate rows.
# Each row of this table indicates that some viewer viewed an article
# (written by some author) on some date.
# Note that equal author_id and viewer_id indicate the same person.
#
# Write a solution to find all the people who viewed more than one article
# on the same date.
#
# Return the result table sorted by id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Views table:
# +------------+-----------+-----------+------------+
# | article_id | author_id | viewer_id | view_date  |
# +------------+-----------+-----------+------------+
# | 1          | 3         | 5         | 2019-08-01 |
# | 3          | 4         | 5         | 2019-08-01 |
# | 1          | 3         | 6         | 2019-08-02 |
# | 2          | 7         | 7         | 2019-08-01 |
# | 2          | 7         | 6         | 2019-08-02 |
# | 4          | 7         | 1         | 2019-07-22 |
# | 3          | 4         | 4         | 2019-07-21 |
# | 3          | 4         | 4         | 2019-07-21 |
# +------------+-----------+-----------+------------+
# Output:
# +------+
# | id   |
# +------+
# | 5    |
# | 6    |
# +------+
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Find viewers who viewed more than one article on the same day.

        Algorithm:
        - GROUP BY viewer_id, view_date HAVING COUNT(DISTINCT article_id) > 1.
        - DISTINCT viewer_id as id, ordered.

        Complexity: O(N).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT DISTINCT viewer_id AS id
    FROM Views
    GROUP BY viewer_id, view_date
    HAVING COUNT(DISTINCT article_id) > 1
    ORDER BY id;
    """
# @lc code=end
