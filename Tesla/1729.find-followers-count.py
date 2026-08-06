#
# @lc app=leetcode id=1729 lang=python3
#
# [1729] Find Followers Count
#
# https://leetcode.com/problems/find-followers-count/description/
#
# algorithms
# Easy (69.62%)
# Likes:    782
# Dislikes: 49
# Total Accepted:    512K
# Total Submissions: 735K
# Testcase Example:  "{\"headers\":{\"Followers\":[\"user_id\",\"follower_id\"]},\"rows\":{\"Followers\":[[\"0\",\"1\"],[\"1\",\"0\"],[\"2\",\"0\"],[\"2\",\"1\"]]}}"
#
# Table: Followers
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | user_id | int |
# | follower_id | int |
# +-------------+------+
# (user_id, follower_id) is the primary key (combination of columns with unique
# values) for this table.
# This table contains the IDs of a user and a follower in a social media app
# where the follower follows the user.
#
# Write a solution that will, for each user, return the number of followers.
#
# Return the result table ordered by user_id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Followers table:
# +---------+-------------+
# | user_id | follower_id |
# +---------+-------------+
# | 0 | 1 |
# | 1 | 0 |
# | 2 | 0 |
# | 2 | 1 |
# +---------+-------------+
# Output:
# +---------+----------------+
# | user_id | followers_count|
# +---------+----------------+
# | 0 | 1 |
# | 1 | 1 |
# | 2 | 2 |
# +---------+----------------+
# Explanation:
# The followers of 0 are {1}
# The followers of 1 are {0}
# The followers of 2 are {0,1}
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Count followers per user_id from Followers table.

        Algorithm:
        - GROUP BY user_id; COUNT(follower_id); ORDER BY user_id.

        Complexity: O(N).
        """
        return self.sql

    sql = """
    SELECT user_id, COUNT(follower_id) AS followers_count
    FROM Followers
    GROUP BY user_id
    ORDER BY user_id;
    """
# @lc code=end
