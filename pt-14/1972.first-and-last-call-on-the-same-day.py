#
# @lc app=leetcode id=1972 lang=python3
#
# [1972] First and Last Call On the Same Day
#
# https://leetcode.com/problems/first-and-last-call-on-the-same-day/description/
#
# database
# Hard (51.03%)
# Likes:    139
# Dislikes: 44
# Total Accepted:    12.7K
# Total Submissions: 25K
# Testcase Example:  "{\"headers\": {\"Calls\": [\"caller_id\", \"recipient_id\", \"call_time\"]}, \"rows\": {\"Calls\": [[8, 4, \"2021-08-24 17:46:07\"], [4, 8, \"2021-08-24 19:57:13\"], [5, 1, \"2021-08-11 05:28:44\"], [8, 3, \"2021-08-17 04:04:15\"], [11, 3, \"2021-08-17 13:07:00\"], [8, 11, \"2021-08-17 22:22:22\"]]}}"
#
#
# Table: Calls
#
# +--------------+----------+
# | Column Name  | Type     |
# +--------------+----------+
# | caller_id    | int      |
# | recipient_id | int      |
# | call_time    | datetime |
# +--------------+----------+
# (caller_id, recipient_id, call_time) is the primary key (combination of
# columns with unique values) for this table.
# Each row contains information about the time of a phone call between
# caller_id and recipient_id.
#
# Write a solution to report the IDs of the users whose first and last
# calls on any day were with the same person. Calls are counted regardless
# of being the caller or the recipient.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Calls table:
# +-----------+--------------+---------------------+
# | caller_id | recipient_id | call_time           |
# +-----------+--------------+---------------------+
# | 8         | 4            | 2021-08-24 17:46:07 |
# | 4         | 8            | 2021-08-24 19:57:13 |
# | 5         | 1            | 2021-08-11 05:28:44 |
# | 8         | 3            | 2021-08-17 04:04:15 |
# | 11        | 3            | 2021-08-17 13:07:00 |
# | 8         | 11           | 2021-08-17 22:22:22 |
# +-----------+--------------+---------------------+
# Output:
# +---------+
# | user_id |
# +---------+
# | 1       |
# | 4       |
# | 5       |
# | 8       |
# +---------+
# Explanation:
# On 2021-08-24, the first and last call of this day for user 8 was with
# user 4. User 8 should be included in the answer.
# Similarly, user 4 on 2021-08-24 had their first and last call with user
# 8. User 4 should be included in the answer.
# On 2021-08-11, user 1 and 5 had a call. This call was the only call for
# both of them on this day. Since this call is the first and last call of
# the day for both of them, they should both be included in the answer.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Find users whose first and last call on some day are with
        the same person (calls are undirected for pairing). Return distinct user_id.

        Algorithm:
        - Normalize each call as (user, other, day, time) both directions.
        - Per (user, day) take FIRST/LAST other by time; keep where equal.

        Complexity: O(C log C) with window/sort.
        """
        return self.sql

    sql = """
    WITH all_calls AS (
        SELECT caller_id AS user_id, recipient_id AS other_id, call_time,
               DATE(call_time) AS day
        FROM Calls
        UNION ALL
        SELECT recipient_id AS user_id, caller_id AS other_id, call_time,
               DATE(call_time) AS day
        FROM Calls
    ),
    ordered AS (
        SELECT user_id, other_id, day,
               FIRST_VALUE(other_id) OVER (
                   PARTITION BY user_id, day ORDER BY call_time
               ) AS first_other,
               FIRST_VALUE(other_id) OVER (
                   PARTITION BY user_id, day ORDER BY call_time DESC
               ) AS last_other
        FROM all_calls
    )
    SELECT DISTINCT user_id
    FROM ordered
    WHERE first_other = last_other
    ORDER BY user_id;
    """

    def solve_agg(self) -> str:
        """
        Interview explanation:
        Alternate: join the day's min-time and max-time call partners per user.

        Algorithm:
        - CTE all_calls; aggregate MIN/MAX(call_time) per user/day; join back
          to get partners; filter equal partners.

        Complexity: O(C log C).
        """
        return self.sql_agg

    sql_agg = """
    WITH all_calls AS (
        SELECT caller_id AS user_id, recipient_id AS other_id, call_time,
               DATE(call_time) AS day
        FROM Calls
        UNION ALL
        SELECT recipient_id AS user_id, caller_id AS other_id, call_time,
               DATE(call_time) AS day
        FROM Calls
    ),
    bounds AS (
        SELECT user_id, day, MIN(call_time) AS first_t, MAX(call_time) AS last_t
        FROM all_calls
        GROUP BY user_id, day
    )
    SELECT DISTINCT b.user_id
    FROM bounds b
    JOIN all_calls f ON f.user_id = b.user_id AND f.day = b.day AND f.call_time = b.first_t
    JOIN all_calls l ON l.user_id = b.user_id AND l.day = b.day AND l.call_time = b.last_t
    WHERE f.other_id = l.other_id
    ORDER BY b.user_id;
    """
# @lc code=end

