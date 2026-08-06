#
# @lc app=leetcode id=586 lang=python3
#
# [586] Customer Placing the Largest Number of Orders
#
# https://leetcode.com/problems/customer-placing-the-largest-number-of-orders/description/
#
# algorithms
# Easy (64.62%)
# Likes:    1251
# Dislikes: 100
# Total Accepted:    562K
# Total Submissions: 870K
# Testcase Example:  "{\"headers\":{\"orders\":[\"order_number\",\"customer_number\"]},\"rows\":{\"orders\":[[1,1],[2,2],[3,3],[4,3]]}}"
#
# Table: Orders
#
# +-----------------+----------+
# | Column Name | Type |
# +-----------------+----------+
# | order_number | int |
# | customer_number | int |
# +-----------------+----------+
# order_number is the primary key (column with unique values) for this table.
# This table contains information about the order ID and the customer ID.
#
# Write a solution to find the customer_number for the customer who has placed
# the largest number of orders.
#
# The test cases are generated so that exactly one customer will have placed
# more orders than any other customer.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Orders table:
# +--------------+-----------------+
# | order_number | customer_number |
# +--------------+-----------------+
# | 1 | 1 |
# | 2 | 2 |
# | 3 | 3 |
# | 4 | 3 |
# +--------------+-----------------+
# Output:
# +-----------------+
# | customer_number |
# +-----------------+
# | 3 |
# +-----------------+
# Explanation:
# The customer with number 3 has two orders, which is greater than either
# customer 1 or 2 because each of them only has one order.
# So the result is customer_number 3.
#
# Follow up: What if more than one customer has the largest number of orders,
# can you find all the customer_number in this case?
#


# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Count orders per customer_number and pick the customer with the
        maximum count (problem guarantees a unique winner in classic version).

        Algorithm:
        - GROUP BY customer_number ORDER BY COUNT(*) DESC LIMIT 1.
        - Or compare count to a MAX subquery if LIMIT is avoided.

        Complexity: O(O) scan/group over Orders.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT customer_number
    FROM Orders
    GROUP BY customer_number
    ORDER BY COUNT(*) DESC
    LIMIT 1;
    """
# @lc code=end

