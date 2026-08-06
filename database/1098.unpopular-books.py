#
# @lc app=leetcode id=1098 lang=python3
#
# [1098] Unpopular Books
#
# https://leetcode.com/problems/unpopular-books/description/
#
# database
# Medium (43.39%)
# Likes:    221
# Dislikes: 623
# Total Accepted:    49.3K
# Total Submissions: 113.5K
# Testcase Example:  "{\"headers\":{\"Books\":[\"book_id\",\"name\",\"available_from\"],\"Orders\":[\"order_id\",\"book_id\",\"quantity\",\"dispatch_date\"]},\"rows\":{\"Books\":[[1,\"Kalila And Demna\",\"2010-01-01\"],[2,\"28 Letters\",\"2012-05-12\"],[3,\"The Hobbit\",\"2019-06-10\"],[4,\"13 Reasons Why\",\"2019-06-01\"],[5,\"The Hunger Games\",\"2008-09-21\"]],\"Orders\":[[1,1,2,\"2018-07-26\"],[2,1,1,\"2018-11-05\"],[3,3,8,\"2019-06-11\"],[4,4,6,\"2019-06-05\"],[5,4,5,\"2019-06-20\"],[6,5,9,\"2009-02-02\"],[7,5,8,\"2010-04-13\"]]}}"
#
#
# Table: Books
#
# +----------------+---------+
# | Column Name    | Type    |
# +----------------+---------+
# | book_id        | int     |
# | name           | varchar |
# | available_from | date    |
# +----------------+---------+
# book_id is the primary key (column with unique values) of this table.
#
# Table: Orders
#
# +----------------+---------+
# | Column Name    | Type    |
# +----------------+---------+
# | order_id       | int     |
# | book_id        | int     |
# | quantity       | int     |
# | dispatch_date  | date    |
# +----------------+---------+
# order_id is the primary key (column with unique values) of this table.
# book_id is a foreign key (reference column) to the Books table.
#
# Write a solution to report the books that have sold less than 10 copies
# in the last year, excluding books that have been available for less than
# one month from today. Assume today is 2019-06-23.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Books table:
# +---------+--------------------+----------------+
# | book_id | name               | available_from |
# +---------+--------------------+----------------+
# | 1       | "Kalila And Demna" | 2010-01-01     |
# | 2       | "28 Letters"       | 2012-05-12     |
# | 3       | "The Hobbit"       | 2019-06-10     |
# | 4       | "13 Reasons Why"   | 2019-06-01     |
# | 5       | "The Hunger Games" | 2008-09-21     |
# +---------+--------------------+----------------+
# Orders table:
# +----------+---------+----------+---------------+
# | order_id | book_id | quantity | dispatch_date |
# +----------+---------+----------+---------------+
# | 1        | 1       | 2        | 2018-07-26    |
# | 2        | 1       | 1        | 2018-11-05    |
# | 3        | 3       | 8        | 2019-06-11    |
# | 4        | 4       | 6        | 2019-06-05    |
# | 5        | 4       | 5        | 2019-06-20    |
# | 6        | 5       | 9        | 2009-02-02    |
# | 7        | 5       | 8        | 2010-04-13    |
# +----------+---------+----------+---------------+
# Output:
# +-----------+--------------------+
# | book_id   | name               |
# +-----------+--------------------+
# | 1         | "Kalila And Demna" |
# | 2         | "28 Letters"       |
# | 5         | "The Hunger Games" |
# +-----------+--------------------+
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Books available for at least 1 month before 2019-06-23 that
        sold fewer than 10 copies in the year ending 2019-06-23
        (dispatch_date in [2018-06-23, 2019-06-23)).

        Algorithm:
        - Filter Books with available_from < '2019-05-23'.
        - LEFT JOIN Orders in the 1-year window; SUM(quantity) < 10 or NULL.

        Complexity: O(B + O) with aggregation.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT b.book_id, b.name
    FROM Books b
    LEFT JOIN Orders o
      ON b.book_id = o.book_id
     AND o.dispatch_date BETWEEN '2018-06-23' AND '2019-06-22'
    WHERE b.available_from < '2019-05-23'
    GROUP BY b.book_id, b.name
    HAVING COALESCE(SUM(o.quantity), 0) < 10;
    """
# @lc code=end
