#
# @lc app=leetcode id=2228 lang=python3
#
# [2228] Users With Two Purchases Within Seven Days
#
# https://leetcode.com/problems/users-with-two-purchases-within-seven-days/description/
#
# database
# Medium (47.03%)
# Likes:    68
# Dislikes: 11
# Total Accepted:    12.5K
# Total Submissions: 26.7K
# Testcase Example:  "{\"headers\":{\"Purchases\":[\"purchase_id\",\"user_id\",\"purchase_date\"]},\"rows\":{\"Purchases\":[[4,2,\"2022-03-13\"],[1,5,\"2022-02-11\"],[3,7,\"2022-06-19\"],[6,2,\"2022-03-20\"],[5,7,\"2022-06-19\"],[2,2,\"2022-06-08\"]]}}"
#
#
# Table: Purchases
#
# +---------------+------+
# | Column Name   | Type |
# +---------------+------+
# | purchase_id   | int  |
# | user_id       | int  |
# | purchase_date | date |
# +---------------+------+
# purchase_id contains unique values.
# This table contains logs of the dates that users purchased from a
# certain retailer.
#
# Write a solution to report the IDs of the users that made any two
# purchases at most 7 days apart.
#
# Return the result table ordered by user_id.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Purchases table:
# +-------------+---------+---------------+
# | purchase_id | user_id | purchase_date |
# +-------------+---------+---------------+
# | 4           | 2       | 2022-03-13    |
# | 1           | 5       | 2022-02-11    |
# | 3           | 7       | 2022-06-19    |
# | 6           | 2       | 2022-03-20    |
# | 5           | 7       | 2022-06-19    |
# | 2           | 2       | 2022-06-08    |
# +-------------+---------+---------------+
# Output:
# +---------+
# | user_id |
# +---------+
# | 2       |
# | 7       |
# +---------+
# Explanation:
# User 2 had two purchases on 2022-03-13 and 2022-03-20. Since the second
# purchase is within 7 days of the first purchase, we add their ID.
# User 5 had only 1 purchase.
# User 7 had two purchases on the same day so we add their ID.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL premium. Purchases(purchase_id, user_id, purchase_date). Users who
        made at least two purchases with |date diff| <= 7 days. Return distinct
        user_id ordered ascending.

        Algorithm:
        - Self-join same user different purchase_id with ABS(DATEDIFF)<=7.

        Complexity: O(N^2) worst / indexed join.
        """
        self.sql = """
SELECT DISTINCT p1.user_id
FROM Purchases p1
JOIN Purchases p2
  ON p1.user_id = p2.user_id
 AND p1.purchase_id <> p2.purchase_id
 AND ABS(DATEDIFF(p1.purchase_date, p2.purchase_date)) <= 7
ORDER BY p1.user_id;
"""
        return self.sql
# @lc code=end
