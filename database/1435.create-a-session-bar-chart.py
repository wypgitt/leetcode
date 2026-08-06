#
# @lc app=leetcode id=1435 lang=python3
#
# [1435] Create a Session Bar Chart
#
# https://leetcode.com/problems/create-a-session-bar-chart/description/
#
# database
# Easy (74.23%)
# Likes:    158
# Dislikes: 266
# Total Accepted:    27.7K
# Total Submissions: 37.3K
# Testcase Example:  "{\"headers\": {\"Sessions\": [\"session_id\", \"duration\"]}, \"rows\": {\"Sessions\": [[1, 30], [2, 199], [3, 299], [4, 580], [5, 1000]]}}"
#
#
# Table: Sessions
#
# +---------------------+---------+
# | Column Name         | Type    |
# +---------------------+---------+
# | session_id          | int     |
# | duration            | int     |
# +---------------------+---------+
# session_id is the column of unique values for this table.
# duration is the time in seconds that a user has visited the application.
#
# You want to know how long a user visits your application. You decided to
# create bins of "[0-5>", "[5-10>", "[10-15>", and "15 minutes or more"
# and count the number of sessions on it.
#
# Write a solution to report the (bin, total).
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Sessions table:
# +-------------+---------------+
# | session_id  | duration      |
# +-------------+---------------+
# | 1           | 30            |
# | 2           | 199           |
# | 3           | 299           |
# | 4           | 580           |
# | 5           | 1000          |
# +-------------+---------------+
# Output:
# +--------------+--------------+
# | bin          | total        |
# +--------------+--------------+
# | [0-5>        | 3            |
# | [5-10>       | 1            |
# | [10-15>      | 0            |
# | 15 or more   | 1            |
# +--------------+--------------+
# Explanation:
# For session_id 1, 2, and 3 have a duration greater or equal than 0
# minutes and less than 5 minutes.
# For session_id 4 has a duration greater or equal than 5 minutes and less
# than 10 minutes.
# There is no session with a duration greater than or equal to 10 minutes
# and less than 15 minutes.
# For session_id 5 has a duration greater than or equal to 15 minutes.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Bin session durations into [0-5>, [5-10>, [10-15>, [15-inf>
        (minutes) and count; always report all 4 bins even if 0.

        Algorithm:
        - UNION ALL four SELECT bin + COUNT with duration filters (seconds).

        Complexity: O(S).
        """
        return self.sql

    sql = """
    SELECT '[0-5>' AS bin, SUM(CASE WHEN duration / 60 < 5 THEN 1 ELSE 0 END) AS total
    FROM Sessions
    UNION ALL
    SELECT '[5-10>' AS bin, SUM(CASE WHEN duration / 60 >= 5 AND duration / 60 < 10 THEN 1 ELSE 0 END) AS total
    FROM Sessions
    UNION ALL
    SELECT '[10-15>' AS bin, SUM(CASE WHEN duration / 60 >= 10 AND duration / 60 < 15 THEN 1 ELSE 0 END) AS total
    FROM Sessions
    UNION ALL
    SELECT '15 or more' AS bin, SUM(CASE WHEN duration / 60 >= 15 THEN 1 ELSE 0 END) AS total
    FROM Sessions;
    """
# @lc code=end
