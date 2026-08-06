#
# @lc app=leetcode id=2993 lang=python3
#
# [2993] Friday Purchases I
#
# https://leetcode.com/problems/friday-purchases-i/description/
#
# database
# Medium (81.10%)
# Likes:    15
# Dislikes: 4
# Total Accepted:    4.5K
# Total Submissions: 5.6K
# Testcase Example:  "{\"headers\":{\"Purchases\":[\"user_id\",\"purchase_date\",\"amount_spend\"]},\"rows\":{\"Purchases\":[[11,\"2023-11-07\",1126],[15,\"2023-11-30\",7473],[17,\"2023-11-14\",2414],[12,\"2023-11-24\",9692],[8,\"2023-11-03\",5117],[1,\"2023-11-16\",5241],[10,\"2023-11-12\",8266],[13,\"2023-11-24\",12000]]}}"
#
#
# Table: Purchases
#
# +---------------+------+
# | Column Name   | Type |
# +---------------+------+
# | user_id       | int  |
# | purchase_date | date |
# | amount_spend  | int  |
# +---------------+------+
# (user_id, purchase_date, amount_spend) is the primary key (combination
# of columns with unique values) for this table.
# purchase_date will range from November 1, 2023, to November 30, 2023,
# inclusive of both dates.
# Each row contains user id, purchase date, and amount spend.
#
# Write a solution to calculate the total spending by users on each Friday
# of every week in November 2023. Output only weeks that include at least
# one purchase on a Friday.
#
# Return the result table ordered by week of month in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Purchases table:
# +---------+---------------+--------------+
# | user_id | purchase_date | amount_spend |
# +---------+---------------+--------------+
# | 11      | 2023-11-07    | 1126         |
# | 15      | 2023-11-30    | 7473         |
# | 17      | 2023-11-14    | 2414         |
# | 12      | 2023-11-24    | 9692         |
# | 8       | 2023-11-03    | 5117         |
# | 1       | 2023-11-16    | 5241         |
# | 10      | 2023-11-12    | 8266         |
# | 13      | 2023-11-24    | 12000        |
# +---------+---------------+--------------+
# Output:
# +---------------+---------------+--------------+
# | week_of_month | purchase_date | total_amount |
# +---------------+---------------+--------------+
# | 1             | 2023-11-03    | 5117         |
# | 4             | 2023-11-24    | 21692        |
# +---------------+---------------+--------------+
# Explanation:
# - During the first week of November 2023, transactions amounting to
# $5,117 occurred on Friday, 2023-11-03.
# - For the second week of November 2023, there were no transactions on
# Friday, 2023-11-10.
# - Similarly, during the third week of November 2023, there were no
# transactions on Friday, 2023-11-17.
# - In the fourth week of November 2023, two transactions took place on
# Friday, 2023-11-24, amounting to $12,000 and $9,692 respectively,
# summing up to a total of $21,692.
# Output table is ordered by week_of_month in ascending order.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Purchases(user_id, purchase_date, amount_spend) in Nov 2023.
        Sum spend per Friday that has purchases; week_of_month = CEIL(day/7).
        Order by week_of_month. (Unlike II, omit Fridays with zero spend.)

        Algorithm:
        - Filter Nov 2023 Fridays (DAYOFWEEK=6); GROUP BY purchase_date; SUM.

        Complexity: O(N).
        """
        self.sql = """
SELECT
    CEIL(DAYOFMONTH(purchase_date) / 7) AS week_of_month,
    purchase_date,
    SUM(amount_spend) AS total_amount
FROM Purchases
WHERE DATE_FORMAT(purchase_date, '%Y%m') = '202311'
  AND DAYOFWEEK(purchase_date) = 6
GROUP BY 2
ORDER BY 1;
"""
        return self.sql
# @lc code=end
