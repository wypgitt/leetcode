#
# @lc app=leetcode id=1821 lang=python3
#
# [1821] Find Customers With Positive Revenue this Year
#
# https://leetcode.com/problems/find-customers-with-positive-revenue-this-year/description/
#
# database
# Easy (87.61%)
# Likes:    66
# Dislikes: 26
# Total Accepted:    38.2K
# Total Submissions: 43.5K
# Testcase Example:  "{\"headers\":{\"Customers\":[\"customer_id\",\"year\",\"revenue\"]},\"rows\":{\"Customers\":[[\"1\",\"2018\",\"50\"],[\"1\",\"2021\",\"30\"],[\"1\",\"2020\",\"70\"],[\"2\",\"2021\",\"-50\"],[\"3\",\"2018\",\"10\"],[\"3\",\"2016\",\"50\"],[\"4\",\"2021\",\"20\"]]}}"
#
#
# Table: Customers
#
# +--------------+------+
# | Column Name  | Type |
# +--------------+------+
# | customer_id  | int  |
# | year         | int  |
# | revenue      | int  |
# +--------------+------+
# (customer_id, year) is the primary key (combination of columns with
# unique values) for this table.
# This table contains the customer ID and the revenue of customers in
# different years.
# Note that this revenue can be negative.
#
# Write a solution to report the customers with postive revenue in the
# year 2021.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Customers table:
# +-------------+------+---------+
# | customer_id | year | revenue |
# +-------------+------+---------+
# | 1           | 2018 | 50      |
# | 1           | 2021 | 30      |
# | 1           | 2020 | 70      |
# | 2           | 2021 | -50     |
# | 3           | 2018 | 10      |
# | 3           | 2016 | 50      |
# | 4           | 2021 | 20      |
# +-------------+------+---------+
# Output:
# +-------------+
# | customer_id |
# +-------------+
# | 1           |
# | 4           |
# +-------------+
# Explanation:
# Customer 1 has revenue equal to 30 in the year 2021.
# Customer 2 has revenue equal to -50 in the year 2021.
# Customer 3 has no revenue in the year 2021.
# Customer 4 has revenue equal to 20 in the year 2021.
# Thus only customers 1 and 4 have positive revenue in the year 2021.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Customers with positive revenue in year 2021.

        Algorithm:
        - SELECT customer_id FROM Customers WHERE year=2021 AND revenue>0.

        Complexity: O(n) scan.
        """
        return self.sql

    sql = """
    SELECT customer_id
    FROM Customers
    WHERE year = 2021 AND revenue > 0;
    """
# @lc code=end
