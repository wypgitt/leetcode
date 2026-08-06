#
# @lc app=leetcode id=1113 lang=python3
#
# [1113] Reported Posts
#
# https://leetcode.com/problems/reported-posts/description/
#
# database
# Easy (64.79%)
# Likes:    119
# Dislikes: 420
# Total Accepted:    54.8K
# Total Submissions: 84.5K
# Testcase Example:  "{\"headers\":{\"Actions\":[\"user_id\",\"post_id\",\"action_date\",\"action\",\"extra\"]},\"rows\":{\"Actions\":[[1,1,\"2019-07-01\",\"view\",null],[1,1,\"2019-07-01\",\"like\",null],[1,1,\"2019-07-01\",\"share\",null],[2,4,\"2019-07-04\",\"view\",null],[2,4,\"2019-07-04\",\"report\",\"spam\"],[3,4,\"2019-07-04\",\"view\",null],[3,4,\"2019-07-04\",\"report\",\"spam\"],[4,3,\"2019-07-02\",\"view\",null],[4,3,\"2019-07-02\",\"report\",\"spam\"],[5,2,\"2019-07-04\",\"view\",null],[5,2,\"2019-07-04\",\"report\",\"racism\"],[5,5,\"2019-07-04\",\"view\",null],[5,5,\"2019-07-04\",\"report\",\"racism\"]]}}"
#
#
# Table: Actions
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | user_id       | int     |
# | post_id       | int     |
# | action_date   | date    |
# | action        | enum    |
# | extra         | varchar |
# +---------------+---------+
# This table may have duplicate rows.
# The action column is an ENUM (category) type of ('view', 'like',
# 'reaction', 'comment', 'report', 'share').
# The extra column has optional information about the action, such as a
# reason for the report or a type of reaction.
#
# Write a solution to report the number of posts reported yesterday for
# each report reason. Assume today is 2019-07-05.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Actions table:
# +---------+---------+-------------+--------+--------+
# | user_id | post_id | action_date | action | extra  |
# +---------+---------+-------------+--------+--------+
# | 1       | 1       | 2019-07-01  | view   | null   |
# | 1       | 1       | 2019-07-01  | like   | null   |
# | 1       | 1       | 2019-07-01  | share  | null   |
# | 2       | 4       | 2019-07-04  | view   | null   |
# | 2       | 4       | 2019-07-04  | report | spam   |
# | 3       | 4       | 2019-07-04  | view   | null   |
# | 3       | 4       | 2019-07-04  | report | spam   |
# | 4       | 3       | 2019-07-02  | view   | null   |
# | 4       | 3       | 2019-07-02  | report | spam   |
# | 5       | 2       | 2019-07-04  | view   | null   |
# | 5       | 2       | 2019-07-04  | report | racism |
# | 5       | 5       | 2019-07-04  | view   | null   |
# | 5       | 5       | 2019-07-04  | report | racism |
# +---------+---------+-------------+--------+--------+
# Output:
# +---------------+--------------+
# | report_reason | report_count |
# +---------------+--------------+
# | spam          | 1            |
# | racism        | 2            |
# +---------------+--------------+
# Explanation: Note that we only care about report reasons with non-zero
# number of reports.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. For reports on 2019-07-04, count distinct posts per report
        reason (extra). Output report_reason and report_count.

        Algorithm:
        - WHERE action = 'report' AND action_date = '2019-07-04'.
        - GROUP BY extra; COUNT(DISTINCT post_id).

        Complexity: O(A) over Actions.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT extra AS report_reason, COUNT(DISTINCT post_id) AS report_count
    FROM Actions
    WHERE action = 'report' AND action_date = '2019-07-04'
    GROUP BY extra;
    """
# @lc code=end
