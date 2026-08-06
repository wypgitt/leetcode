#
# @lc app=leetcode id=1193 lang=python3
#
# [1193] Monthly Transactions I
#
# https://leetcode.com/problems/monthly-transactions-i/description/
#
# algorithms
# Medium (59.61%)
# Likes:    1498
# Dislikes: 135
# Total Accepted:    591K
# Total Submissions: 991K
# Testcase Example:  "{\"headers\":{\"Transactions\":[\"id\",\"country\",\"state\",\"amount\",\"trans_date\"]},\"rows\":{\"Transactions\":[[121,\"US\",\"approved\",1000,\"2018-12-18\"],[122,\"US\",\"declined\",2000,\"2018-12-19\"],[123,\"US\",\"approved\",2000,\"2019-01-01\"],[124,\"DE\",\"approved\",2000,\"2019-01-07\"]]}}"
#
# Table: Transactions
#
# +---------------+---------+
# | Column Name | Type |
# +---------------+---------+
# | id | int |
# | country | varchar |
# | state | enum |
# | amount | int |
# | trans_date | date |
# +---------------+---------+
# id is the primary key of this table.
# The table has information about incoming transactions.
# The state column is an enum of type ["approved", "declined"].
#
# Write an SQL query to find for each month and country, the number of
# transactions and their total amount, the number of approved transactions and
# their total amount.
#
# Return the result table in any order.
#
# The query result format is in the following example.
#
# Example 1:
#
# Input:
# Transactions table:
# +------+---------+----------+--------+------------+
# | id | country | state | amount | trans_date |
# +------+---------+----------+--------+------------+
# | 121 | US | approved | 1000 | 2018-12-18 |
# | 122 | US | declined | 2000 | 2018-12-19 |
# | 123 | US | approved | 2000 | 2019-01-01 |
# | 124 | DE | approved | 2000 | 2019-01-07 |
# +------+---------+----------+--------+------------+
# Output:
# +----------+---------+-------------+----------------+--------------------+-----------------------+
# | month | country | trans_count | approved_count | trans_total_amount |
# approved_total_amount |
# +----------+---------+-------------+----------------+--------------------+-----------------------+
# | 2018-12 | US | 2 | 1 | 3000 | 1000 |
# | 2019-01 | US | 1 | 1 | 2000 | 2000 |
# | 2019-01 | DE | 1 | 1 | 2000 | 2000 |
# +----------+---------+-------------+----------------+--------------------+-----------------------+
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Per (month, country): count all transactions and approved ones, and
        sum amounts for each. Month from DATE_FORMAT(trans_date, '%Y-%m').

        Algorithm:
        - GROUP BY month, country with COUNT(*), SUM(amount), and conditional
          COUNT/SUM for state='approved'.

        Complexity: O(N) aggregation.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        DATE_FORMAT(trans_date, '%Y-%m') AS month,
        country,
        COUNT(*) AS trans_count,
        SUM(state = 'approved') AS approved_count,
        SUM(amount) AS trans_total_amount,
        SUM(IF(state = 'approved', amount, 0)) AS approved_total_amount
    FROM Transactions
    GROUP BY month, country;
    """
# @lc code=end
