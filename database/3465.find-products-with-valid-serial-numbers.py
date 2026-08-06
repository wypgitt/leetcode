#
# @lc app=leetcode id=3465 lang=python3
#
# [3465] Find Products with Valid Serial Numbers
#
# https://leetcode.com/problems/find-products-with-valid-serial-numbers/description/
#
# database
# Easy (28.84%)
# Likes:    60
# Dislikes: 29
# Total Accepted:    24.9K
# Total Submissions: 86.3K
# Testcase Example:  "{\"headers\":{\"products\":[\"product_id\",\"product_name\",\"description\"]},\"rows\":{\"products\":[[1,\"Widget A\",\"This is a sample product with SN1234-5678\"],[2,\"Widget B\",\"A product with serial SN9876-1234 in the description\"],[3,\"Widget C\",\"Product SN1234-56789 is available now\"],[4,\"Widget D\",\"No serial number here\"],[5,\"Widget E\",\"Check out SN4321-8765 in this description\"]]}}"
#
#
# Table: products
#
# +--------------+------------+
# | Column Name  | Type       |
# +--------------+------------+
# | product_id   | int        |
# | product_name | varchar    |
# | description  | varchar    |
# +--------------+------------+
# (product_id) is the unique key for this table.
# Each row in the table represents a product with its unique ID, name, and
# description.
#
# Write a solution to find all products whose description contains a valid
# serial number pattern. A valid serial number follows these rules:
#
# It starts with the letters SN (case-sensitive).
#
# Followed by exactly 4 digits.
#
# It must have a hyphen (-) followed by exactly 4 digits.
#
# The serial number must be within the description (it may not necessarily
# start at the beginning).
#
# Return the result table ordered by product_id in ascending order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# products table:
#
# +------------+--------------+------------------------------------------------------+
# | product_id | product_name | description
# |
# +------------+--------------+------------------------------------------------------+
# | 1          | Widget A     | This is a sample product with SN1234-5678
# |
# | 2          | Widget B     | A product with serial SN9876-1234 in the
# description |
# | 3          | Widget C     | Product SN1234-56789 is available now
# |
# | 4          | Widget D     | No serial number here
# |
# | 5          | Widget E     | Check out SN4321-8765 in this description
# |
# +------------+--------------+------------------------------------------------------+
#
# Output:
#
# +------------+--------------+------------------------------------------------------+
# | product_id | product_name | description
# |
# +------------+--------------+------------------------------------------------------+
# | 1          | Widget A     | This is a sample product with SN1234-5678
# |
# | 2          | Widget B     | A product with serial SN9876-1234 in the
# description |
# | 5          | Widget E     | Check out SN4321-8765 in this description
# |
# +------------+--------------+------------------------------------------------------+
#
# Explanation:
#
# Product 1: Valid serial number SN1234-5678
#
# Product 2: Valid serial number SN9876-1234
#
# Product 3: Invalid serial number SN1234-56789 (contains 5 digits after
# the hyphen)
#
# Product 4: No serial number in the description
#
# Product 5: Valid serial number SN4321-8765
#
# The result table is ordered by product_id in ascending order.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Find products whose description contains a standalone serial of the
        form SN####-#### (exactly four digits on each side of the hyphen).

        Algorithm:
        - REGEXP with word boundaries around SN[0-9]{4}-[0-9]{4}.
        - ORDER BY product_id ascending.

        Complexity: O(N * L) regex scan over description lengths.
        """
        self.sql = """
SELECT
    product_id,
    product_name,
    description
FROM products
WHERE description REGEXP '\\bSN[0-9]{4}-[0-9]{4}\\b'
ORDER BY product_id;
"""
        return self.sql
# @lc code=end

