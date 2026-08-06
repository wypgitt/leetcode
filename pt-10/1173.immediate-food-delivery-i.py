#
# @lc app=leetcode id=1173 lang=python3
#
# [1173] Immediate Food Delivery I
#
# https://leetcode.com/problems/immediate-food-delivery-i/description/
#
# database
# Easy (80.58%)
# Likes:    305
# Dislikes: 13
# Total Accepted:    93.5K
# Total Submissions: 116K
# Testcase Example:  "{\"headers\":{\"Delivery\":[\"delivery_id\",\"customer_id\",\"order_date\",\"customer_pref_delivery_date\"]},\"rows\":{\"Delivery\":[[1,1,\"2019-08-01\",\"2019-08-02\"],[2,5,\"2019-08-02\",\"2019-08-02\"],[3,1,\"2019-08-11\",\"2019-08-11\"],[4,3,\"2019-08-24\",\"2019-08-26\"],[5,4,\"2019-08-21\",\"2019-08-22\"],[6,2,\"2019-08-11\",\"2019-08-13\"]]}}"
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
# delivery_id is the primary key (column with unique values) of this
# table.
# The table holds information about food delivery to customers that make
# orders at some date and specify a preferred delivery date (on the same
# order date or after it).
#
# If the customer's preferred delivery date is the same as the order date,
# then the order is called immediate; otherwise, it is called scheduled.
#
# Write a solution to find the percentage of immediate orders in the
# table, rounded to 2 decimal places.
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
# | 2           | 5           | 2019-08-02 | 2019-08-02                  |
# | 3           | 1           | 2019-08-11 | 2019-08-11                  |
# | 4           | 3           | 2019-08-24 | 2019-08-26                  |
# | 5           | 4           | 2019-08-21 | 2019-08-22                  |
# | 6           | 2           | 2019-08-11 | 2019-08-13                  |
# +-------------+-------------+------------+-----------------------------+
# Output:
# +----------------------+
# | immediate_percentage |
# +----------------------+
# | 33.33                |
# +----------------------+
# Explanation: The orders with delivery id 2 and 3 are immediate while the
# others are scheduled.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: percentage of immediate deliveries (order_date equals
        preferred date) among all rows, rounded to 2 decimals.

        Algorithm:
        - AVG/SUM of (order_date = customer_pref_delivery_date) * 100, ROUND 2.

        Complexity: O(N) scan.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT ROUND(
        100.0 * SUM(order_date = customer_pref_delivery_date) / COUNT(*),
        2
    ) AS immediate_percentage
    FROM Delivery;
    """
# @lc code=end
