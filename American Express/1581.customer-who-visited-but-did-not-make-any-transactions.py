#
# @lc app=leetcode id=1581 lang=python3
#
# [1581] Customer Who Visited but Did Not Make Any Transactions
#
# https://leetcode.com/problems/customer-who-visited-but-did-not-make-any-transactions/description/
#
# algorithms
# Easy (68.19%)
# Likes:    3608
# Dislikes: 463
# Total Accepted:    1.2M
# Total Submissions: 1.8M
# Testcase Example:  "{\"headers\":{\"Visits\":[\"visit_id\",\"customer_id\"],\"Transactions\":[\"transaction_id\",\"visit_id\",\"amount\"]},\"rows\":{\"Visits\":[[1,23],[2,9],[4,30],[5,54],[6,96],[7,54],[8,54]],\"Transactions\":[[2,5,310],[3,5,300],[9,5,200],[12,1,910],[13,2,970]]}}"
#
# Table: Visits
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | visit_id | int |
# | customer_id | int |
# +-------------+---------+
# visit_id is the column with unique values for this table.
# This table contains information about the customers who visited the mall.
#
# Table: Transactions
#
# +----------------+---------+
# | Column Name | Type |
# +----------------+---------+
# | transaction_id | int |
# | visit_id | int |
# | amount | int |
# +----------------+---------+
# transaction_id is column with unique values for this table.
# This table contains information about the transactions made during the
# visit_id.
#
# Write a solution to find the IDs of the users who visited without making any
# transactions and the number of times they made these types of visits.
#
# Return the result table sorted in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Visits
# +----------+-------------+
# | visit_id | customer_id |
# +----------+-------------+
# | 1 | 23 |
# | 2 | 9 |
# | 4 | 30 |
# | 5 | 54 |
# | 6 | 96 |
# | 7 | 54 |
# | 8 | 54 |
# +----------+-------------+
# Transactions
# +----------------+----------+--------+
# | transaction_id | visit_id | amount |
# +----------------+----------+--------+
# | 2 | 5 | 310 |
# | 3 | 5 | 300 |
# | 9 | 5 | 200 |
# | 12 | 1 | 910 |
# | 13 | 2 | 970 |
# +----------------+----------+--------+
# Output:
# +-------------+----------------+
# | customer_id | count_no_trans |
# +-------------+----------------+
# | 54 | 2 |
# | 30 | 1 |
# | 96 | 1 |
# +-------------+----------------+
# Explanation:
# Customer with id = 23 visited the mall once and made one transaction during
# the visit with id = 12.
# Customer with id = 9 visited the mall once and made one transaction during
# the visit with id = 13.
# Customer with id = 30 visited the mall once and did not make any
# transactions.
# Customer with id = 54 visited the mall three times. During 2 visits they did
# not make any transactions, and during one visit they made 3 transactions.
# Customer with id = 96 visited the mall once and did not make any
# transactions.
# As we can see, users with IDs 30 and 96 visited the mall one time without
# making any transactions. Also, user 54 visited the mall twice and did not
# make any transactions.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Visits without any transaction: LEFT JOIN Transactions and keep NULL
        transaction_id; GROUP BY customer_id counting such visits.

        Algorithm:
        - FROM Visits v LEFT JOIN Transactions t ON visit_id
        - WHERE t.transaction_id IS NULL
        - GROUP BY customer_id; COUNT(*) AS count_no_trans

        Complexity: O(V + T) with hash join.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT v.customer_id, COUNT(*) AS count_no_trans
    FROM Visits v
    LEFT JOIN Transactions t ON v.visit_id = t.visit_id
    WHERE t.transaction_id IS NULL
    GROUP BY v.customer_id;
    """
# @lc code=end

