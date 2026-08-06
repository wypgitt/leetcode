#
# @lc app=leetcode id=597 lang=python3
#
# [597] Friend Requests I: Overall Acceptance Rate
#
# https://leetcode.com/problems/friend-requests-i-overall-acceptance-rate/description/
#
# database
# Easy (41.02%)
# Likes:    321
# Dislikes: 779
# Total Accepted:    87.7K
# Total Submissions: 213.8K
# Testcase Example:  "{\"headers\":{\"FriendRequest\":[\"sender_id\",\"send_to_id\",\"request_date\"],\"RequestAccepted\":[\"requester_id\",\"accepter_id\",\"accept_date\"]},\"rows\":{\"FriendRequest\":[[1,2,\"2016/06/01\"],[1,3,\"2016/06/01\"],[1,4,\"2016/06/01\"],[2,3,\"2016/06/02\"],[3,4,\"2016/06/09\"]],\"RequestAccepted\":[[1,2,\"2016/06/03\"],[1,3,\"2016/06/08\"],[2,3,\"2016/06/08\"],[3,4,\"2016/06/09\"],[3,4,\"2016/06/10\"]]}}"
#
#
# Table: FriendRequest
#
# +----------------+---------+
# | Column Name    | Type    |
# +----------------+---------+
# | sender_id      | int     |
# | send_to_id     | int     |
# | request_date   | date    |
# +----------------+---------+
# This table may contain duplicates (In other words, there is no primary
# key for this table in SQL).
# This table contains the ID of the user who sent the request, the ID of
# the user who received the request, and the date of the request.
#
# Table: RequestAccepted
#
# +----------------+---------+
# | Column Name    | Type    |
# +----------------+---------+
# | requester_id   | int     |
# | accepter_id    | int     |
# | accept_date    | date    |
# +----------------+---------+
# This table may contain duplicates (In other words, there is no primary
# key for this table in SQL).
# This table contains the ID of the user who sent the request, the ID of
# the user who received the request, and the date when the request was
# accepted.
#
# Find the overall acceptance rate of requests, which is the number of
# acceptance divided by the number of requests. Return the answer rounded
# to 2 decimals places.
#
# Note that:
#
# The accepted requests are not necessarily from the table friend_request.
# In this case, Count the total accepted requests (no matter whether they
# are in the original requests), and divide it by the number of requests
# to get the acceptance rate.
#
# It is possible that a sender sends multiple requests to the same
# receiver, and a request could be accepted more than once. In this case,
# the ‘duplicated’ requests or acceptances are only counted once.
#
# If there are no requests at all, you should return 0.00 as the
# accept_rate.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# FriendRequest table:
# +-----------+------------+--------------+
# | sender_id | send_to_id | request_date |
# +-----------+------------+--------------+
# | 1         | 2          | 2016/06/01   |
# | 1         | 3          | 2016/06/01   |
# | 1         | 4          | 2016/06/01   |
# | 2         | 3          | 2016/06/02   |
# | 3         | 4          | 2016/06/09   |
# +-----------+------------+--------------+
# RequestAccepted table:
# +--------------+-------------+-------------+
# | requester_id | accepter_id | accept_date |
# +--------------+-------------+-------------+
# | 1            | 2           | 2016/06/03  |
# | 1            | 3           | 2016/06/08  |
# | 2            | 3           | 2016/06/08  |
# | 3            | 4           | 2016/06/09  |
# | 3            | 4           | 2016/06/10  |
# +--------------+-------------+-------------+
# Output:
# +-------------+
# | accept_rate |
# +-------------+
# | 0.8         |
# +-------------+
# Explanation:
# There are 4 unique accepted requests, and there are 5 requests in total.
# So the rate is 0.80.
#
# Follow up:
#
# Could you find the acceptance rate for every month?
#
# Could you find the cumulative acceptance rate for every day?
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium: overall acceptance rate = (# distinct accepted pairs) /
        (# distinct requested pairs), rounded to 2 decimals. Duplicate
        request/accept rows for the same pair count once. If no requests,
        rate is 0.00.

        Algorithm:
        - accepted = COUNT(DISTINCT requester_id, accepter_id) from RequestAccepted.
        - requested = COUNT(DISTINCT sender_id, send_to_id) from FriendRequest.
        - ROUND(IFNULL(accepted/requested, 0), 2) AS accept_rate.

        Complexity: O(R + A) over request/accept tables.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        ROUND(
            IFNULL(
                (
                    SELECT COUNT(DISTINCT requester_id, accepter_id)
                    FROM RequestAccepted
                ) / (
                    SELECT COUNT(DISTINCT sender_id, send_to_id)
                    FROM FriendRequest
                ),
                0
            ),
            2
        ) AS accept_rate;
    """
# @lc code=end

