#
# @lc app=leetcode id=2752 lang=python3
#
# [2752] Customers with Maximum Number of Transactions on Consecutive Days
#
# https://leetcode.com/problems/customers-with-maximum-number-of-transactions-on-consecutive-days/description/
#
# database
# Hard (42.39%)
# Likes:    16
# Dislikes: 35
# Total Accepted:    3.4K
# Total Submissions: 7.9K
# Testcase Example:  "{\"headers\":{\"Transactions\":[\"transaction_id\",\"customer_id\",\"transaction_date\",\"amount\"]},\"rows\":{\"Transactions\":[[1,101,\"2023-05-01\",100],[2,101,\"2023-05-02\",150],[3,101,\"2023-05-03\",200],[4,102,\"2023-05-01\",50],[5,102,\"2023-05-03\",100],[6,102,\"2023-05-04\",200],[7,105,\"2023-05-01\",100],[8,105,\"2023-05-02\",150],[9,105,\"2023-05-03\",200]]}}"
#
#
# Table: Transactions
#
# +------------------+------+
# | Column Name      | Type |
# +------------------+------+
# | transaction_id   | int  |
# | customer_id      | int  |
# | transaction_date | date |
# | amount           | int  |
# +------------------+------+
# transaction_id is the column with unique values of this table.
# Each row contains information about transactions that includes unique
# (customer_id, transaction_date) along with the corresponding customer_id
# and amount.
#
# Write a solution to find all customer_id who made the maximum number of
# transactions on consecutive days.
#
# Return all customer_id with the maximum number of consecutive
# transactions. Order the result table by customer_id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Transactions table:
# +----------------+-------------+------------------+--------+
# | transaction_id | customer_id | transaction_date | amount |
# +----------------+-------------+------------------+--------+
# | 1              | 101         | 2023-05-01       | 100    |
# | 2              | 101         | 2023-05-02       | 150    |
# | 3              | 101         | 2023-05-03       | 200    |
# | 4              | 102         | 2023-05-01       | 50     |
# | 5              | 102         | 2023-05-03       | 100    |
# | 6              | 102         | 2023-05-04       | 200    |
# | 7              | 105         | 2023-05-01       | 100    |
# | 8              | 105         | 2023-05-02       | 150    |
# | 9              | 105         | 2023-05-03       | 200    |
# +----------------+-------------+------------------+--------+
# Output:
# +-------------+
# | customer_id |
# +-------------+
# | 101         |
# | 105         |
# +-------------+
# Explanation:
# - customer_id 101 has a total of 3 transactions, and all of them are
# consecutive.
# - customer_id 102 has a total of 3 transactions, but only 2 of them are
# consecutive.
# - customer_id 105 has a total of 3 transactions, and all of them are
# consecutive.
# In total, the highest number of consecutive transactions is 3, achieved
# by customer_id 101 and 105. The customer_id are sorted in ascending
# order.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Transactions(transaction_id, customer_id, transaction_date,
        amount) with unique (customer_id, transaction_date). Find customers with
        the maximum streak of consecutive daily transactions. Order by
        customer_id ascending.

        Algorithm:
        - Tag consecutive runs with DATE_SUB(date, INTERVAL ROW_NUMBER() DAY);
          count per (customer, group); select customers with count = MAX(count).

        Complexity: O(N log N).
        """
        self.sql = """
WITH
  s AS (
    SELECT
      customer_id,
      DATE_SUB(
        transaction_date,
        INTERVAL ROW_NUMBER() OVER (
          PARTITION BY customer_id
          ORDER BY transaction_date
        ) DAY
      ) AS grp
    FROM Transactions
  ),
  t AS (
    SELECT customer_id, COUNT(1) AS cnt
    FROM s
    GROUP BY customer_id, grp
  )
SELECT customer_id
FROM t
WHERE cnt = (SELECT MAX(cnt) FROM t)
ORDER BY customer_id;
"""
        return self.sql
# @lc code=end
