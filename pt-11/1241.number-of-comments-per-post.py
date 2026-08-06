#
# @lc app=leetcode id=1241 lang=python3
#
# [1241] Number of Comments per Post
#
# https://leetcode.com/problems/number-of-comments-per-post/description/
#
# database
# Easy (65.56%)
# Likes:    187
# Dislikes: 547
# Total Accepted:    41.7K
# Total Submissions: 63.6K
# Testcase Example:  "{\"headers\":{\"Submissions\":[\"sub_id\",\"parent_id\"]},\"rows\":{\"Submissions\":[[1,null],[2,null],[1,null],[12,null],[3,1],[5,2],[3,1],[4,1],[9,1],[10,2],[6,7]]}}"
#
#
# Table: Submissions
#
# +---------------+----------+
# | Column Name   | Type     |
# +---------------+----------+
# | sub_id        | int      |
# | parent_id     | int      |
# +---------------+----------+
# This table may have duplicate rows.
# Each row can be a post or comment on the post.
# parent_id is null for posts.
# parent_id for comments is sub_id for another post in the table.
#
# Write a solution to find the number of comments per post. The result
# table should contain post_id and its corresponding number_of_comments.
#
# The Submissions table may contain duplicate comments. You should count
# the number of unique comments per post.
#
# The Submissions table may contain duplicate posts. You should treat them
# as one post.
#
# The result table should be ordered by post_id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Submissions table:
# +---------+------------+
# | sub_id  | parent_id  |
# +---------+------------+
# | 1       | Null       |
# | 2       | Null       |
# | 1       | Null       |
# | 12      | Null       |
# | 3       | 1          |
# | 5       | 2          |
# | 3       | 1          |
# | 4       | 1          |
# | 9       | 1          |
# | 10      | 2          |
# | 6       | 7          |
# +---------+------------+
# Output:
# +---------+--------------------+
# | post_id | number_of_comments |
# +---------+--------------------+
# | 1       | 3                  |
# | 2       | 2                  |
# | 12      | 0                  |
# +---------+--------------------+
# Explanation:
# The post with id 1 has three comments in the table with id 3, 4, and 9.
# The comment with id 3 is repeated in the table, we counted it only once.
# The post with id 2 has two comments in the table with id 5 and 10.
# The post with id 12 has no comments in the table.
# The comment with id 6 is a comment on a deleted post with id 7 so we
# ignored it.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Posts are submissions with parent_id NULL. Count distinct
        comment sub_ids per post (parent_id = post). Include posts with 0 comments.

        Algorithm:
        - Posts CTE: DISTINCT sub_id WHERE parent_id IS NULL
        - LEFT JOIN Submissions on parent_id = post; COUNT DISTINCT comment id

        Complexity: O(N).
        """
        return self.sql

    sql = """
    SELECT p.sub_id AS post_id,
           COUNT(DISTINCT c.sub_id) AS number_of_comments
    FROM (
        SELECT DISTINCT sub_id
        FROM Submissions
        WHERE parent_id IS NULL
    ) p
    LEFT JOIN Submissions c ON c.parent_id = p.sub_id
    GROUP BY p.sub_id
    ORDER BY post_id;
    """
# @lc code=end
