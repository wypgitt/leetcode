#
# @lc app=leetcode id=1205 lang=python3
#
# [1205] Monthly Transactions II
#
# https://leetcode.com/problems/monthly-transactions-ii/description/
#
# database
# Medium (42.03%)
# Likes:    163
# Dislikes: 557
# Total Accepted:    29K
# Total Submissions: 69.1K
# Testcase Example:  "{\"headers\":{\"Transactions\":[\"id\",\"country\",\"state\",\"amount\",\"trans_date\"],\"Chargebacks\":[\"trans_id\",\"trans_date\"]},\"rows\":{\"Transactions\":[[101,\"US\",\"approved\",1000,\"2019-05-18\"],[102,\"US\",\"declined\",2000,\"2019-05-19\"],[103,\"US\",\"approved\",3000,\"2019-06-10\"],[104,\"US\",\"declined\",4000,\"2019-06-13\"],[105,\"US\",\"approved\",5000,\"2019-06-15\"]],\"Chargebacks\":[[102,\"2019-05-29\"],[101,\"2019-06-30\"],[105,\"2019-09-18\"]]}}"
#
#
# Table: Transactions
#
# +----------------+---------+
# | Column Name    | Type    |
# +----------------+---------+
# | id             | int     |
# | country        | varchar |
# | state          | enum    |
# | amount         | int     |
# | trans_date     | date    |
# +----------------+---------+
# id is the column of unique values of this table.
# The table has information about incoming transactions.
# The state column is an ENUM (category) of type ["approved", "declined"].
#
# Table: Chargebacks
#
# +----------------+---------+
# | Column Name    | Type    |
# +----------------+---------+
# | trans_id       | int     |
# | trans_date     | date    |
# +----------------+---------+
# Chargebacks contains basic information regarding incoming chargebacks
# from some transactions placed in Transactions table.
# trans_id is a foreign key (reference column) to the id column of
# Transactions table.
# Each chargeback corresponds to a transaction made previously even if
# they were not approved.
#
# Write a solution to find for each month and country: the number of
# approved transactions and their total amount, the number of chargebacks,
# and their total amount.
#
# Note: In your solution, given the month and country, ignore rows with
# all zeros.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Transactions table:
# +-----+---------+----------+--------+------------+
# | id  | country | state    | amount | trans_date |
# +-----+---------+----------+--------+------------+
# | 101 | US      | approved | 1000   | 2019-05-18 |
# | 102 | US      | declined | 2000   | 2019-05-19 |
# | 103 | US      | approved | 3000   | 2019-06-10 |
# | 104 | US      | declined | 4000   | 2019-06-13 |
# | 105 | US      | approved | 5000   | 2019-06-15 |
# +-----+---------+----------+--------+------------+
# Chargebacks table:
# +----------+------------+
# | trans_id | trans_date |
# +----------+------------+
# | 102      | 2019-05-29 |
# | 101      | 2019-06-30 |
# | 105      | 2019-09-18 |
# +----------+------------+
# Output:
# +---------+---------+----------------+-----------------+------------------+-------------------+
# | month   | country | approved_count | approved_amount |
# chargeback_count | chargeback_amount |
# +---------+---------+----------------+-----------------+------------------+-------------------+
# | 2019-05 | US      | 1              | 1000            | 1
# | 2000              |
# | 2019-06 | US      | 2              | 8000            | 1
# | 1000              |
# | 2019-09 | US      | 0              | 0               | 1
# | 5000              |
# +---------+---------+----------------+-----------------+------------------+-------------------+
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. For each month and country report approved count/amount
        and chargeback count/amount. Chargebacks use chargeback date and join
        to original transaction country/amount. Include months with only
        chargebacks.

        Algorithm:
        - UNION ALL approved txs (by trans_date) and chargebacks (by cb date)
        - Aggregate by month,country for approved_* and chargeback_*

        Complexity: O(N) scan after joins.
        """
        return self.sql

    sql = """
    SELECT month, country,
           SUM(approved_count) AS approved_count,
           SUM(approved_amount) AS approved_amount,
           SUM(chargeback_count) AS chargeback_count,
           SUM(chargeback_amount) AS chargeback_amount
    FROM (
        SELECT DATE_FORMAT(trans_date, '%Y-%m') AS month,
               country,
               1 AS approved_count,
               amount AS approved_amount,
               0 AS chargeback_count,
               0 AS chargeback_amount
        FROM Transactions
        WHERE state = 'approved'
        UNION ALL
        SELECT DATE_FORMAT(c.trans_date, '%Y-%m') AS month,
               t.country,
               0 AS approved_count,
               0 AS approved_amount,
               1 AS chargeback_count,
               t.amount AS chargeback_amount
        FROM Chargebacks c
        JOIN Transactions t ON c.trans_id = t.id
    ) u
    GROUP BY month, country;
    """
# @lc code=end
