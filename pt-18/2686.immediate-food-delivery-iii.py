#
# @lc app=leetcode id=2686 lang=python3
#
# [2686] Immediate Food Delivery III
#
# https://leetcode.com/problems/immediate-food-delivery-iii/description/
#
# database
# Medium (70.39%)
# Likes:    16
# Dislikes: 1
# Total Accepted:    6.1K
# Total Submissions: 8.7K
# Testcase Example:  "{\"headers\":{\"Delivery\":[\"delivery_id\",\"customer_id\",\"order_date\",\"customer_pref_delivery_date\"]},\"rows\":{\"Delivery\":[[1,1,\"2019-08-01\",\"2019-08-02\"],[2,2,\"2019-08-01\",\"2019-08-01\"],[3,1,\"2019-08-01\",\"2019-08-01\"],[4,3,\"2019-08-02\",\"2019-08-13\"],[5,3,\"2019-08-02\",\"2019-08-02\"],[6,2,\"2019-08-02\",\"2019-08-02\"],[7,4,\"2019-08-03\",\"2019-08-03\"],[8,1,\"2019-08-03\",\"2019-08-03\"],[9,5,\"2019-08-04\",\"2019-08-18\"],[10,2,\"2019-08-04\",\"2019-08-18\"]]}}"
#
#
# Table: Delivery
#
# +-----------------------------+---------+
# | Column Name                 | Type    |
# +-----------------------------+---------+
# | delivery_id                 | int     |
# | customer_id                 | int     |
# | order_date                  | date    |
# | customer_pref_delivery_date | date    |
# +-----------------------------+---------+
# delivery_id is the column with unique values of this table.
# Each row contains information about food delivery to a customer that
# makes an order at some date and specifies a preferred delivery date (on
# the order date or after it).
#
# If the customer's preferred delivery date is the same as the order date,
# then the order is called immediate, otherwise, it is scheduled.
#
# Write a solution to find the percentage of immediate orders on each
# unique order_date, rounded to 2 decimal places.
#
# Return the result table ordered by order_date in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Delivery table:
# +-------------+-------------+------------+-----------------------------+
# | delivery_id | customer_id | order_date | customer_pref_delivery_date |
# +-------------+-------------+------------+-----------------------------+
# | 1           | 1           | 2019-08-01 | 2019-08-02                  |
# | 2           | 2           | 2019-08-01 | 2019-08-01                  |
# | 3           | 1           | 2019-08-01 | 2019-08-01                  |
# | 4           | 3           | 2019-08-02 | 2019-08-13                  |
# | 5           | 3           | 2019-08-02 | 2019-08-02                  |
# | 6           | 2           | 2019-08-02 | 2019-08-02                  |
# | 7           | 4           | 2019-08-03 | 2019-08-03                  |
# | 8           | 1           | 2019-08-03 | 2019-08-03                  |
# | 9           | 5           | 2019-08-04 | 2019-08-08                  |
# | 10          | 2           | 2019-08-04 | 2019-08-18                  |
# +-------------+-------------+------------+-----------------------------+
# Output:
# +------------+----------------------+
# | order_date | immediate_percentage |
# +------------+----------------------+
# | 2019-08-01 | 66.67                |
# | 2019-08-02 | 66.67                |
# | 2019-08-03 | 100.00               |
# | 2019-08-04 | 0.00                 |
# +------------+----------------------+
# Explanation:
# - On 2019-08-01 there were three orders, out of those, two were
# immediate and one was scheduled. So, immediate percentage for that date
# was 66.67.
# - On 2019-08-02 there were three orders, out of those, two were
# immediate and one was scheduled. So, immediate percentage for that date
# was 66.67.
# - On 2019-08-03 there were two orders, both were immediate. So, the
# immediate percentage for that date was 100.00.
# - On 2019-08-04 there were two orders, both were scheduled. So, the
# immediate percentage for that date was 0.00.
# order_date is sorted in ascending order.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Delivery(delivery_id, customer_id, order_date, customer_pref_delivery_date).
        Immediate iff pref date equals order date. For each order_date, percentage of immediate
        orders rounded to 2 decimals; order by order_date ASC.

        Algorithm:
        - GROUP BY order_date; ROUND(100 * SUM(immediate)/COUNT(*), 2).

        Complexity: O(N).
        """
        self.sql = """
SELECT
  order_date,
  ROUND(
    100 * SUM(IF(customer_pref_delivery_date = order_date, 1, 0)) / COUNT(*),
    2
  ) AS immediate_percentage
FROM Delivery
GROUP BY order_date
ORDER BY order_date;
"""
        return self.sql
# @lc code=end
