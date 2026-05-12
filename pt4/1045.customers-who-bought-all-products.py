#
# @lc app=leetcode id=1045 lang=mysql
#
# [1045] Customers Who Bought All Products
#

SQL_SOLUTION = """
SELECT
    customer_id
FROM
    Customer
GROUP BY
    customer_id
HAVING
    COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product);
"""

"""
Interview Explanation

Core idea:
A customer qualifies if the number of distinct products they bought equals the
total number of products in the Product table.

SQL:
SELECT customer_id
FROM Customer
GROUP BY customer_id
HAVING COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product);

Why COUNT(DISTINCT):
The Customer table can contain repeated purchases. Buying the same product
multiple times should still count as owning only one required product, so
COUNT(DISTINCT product_key) is the correct aggregate.

Why GROUP BY:
The condition is per customer, so we group all purchase rows by customer_id and
evaluate the aggregate for each group.

Correctness:
The subquery returns the total number of products that must be covered. For
each customer group, COUNT(DISTINCT product_key) counts exactly how many unique
required product keys that customer has bought. Equality holds exactly for
customers who bought every product.

Complexity:
Conceptually, the database scans Customer, groups by customer_id, and counts
distinct product keys per group. Runtime depends on indexes and query engine,
but a useful index is Customer(customer_id, product_key). Product is scanned
once for its count.

Tests and edge cases:
- Duplicate purchases do not inflate the count.
- A customer missing one product is filtered out.
- A customer with exactly all products is returned.
- If Product has one row, every customer who bought that product qualifies.

Note:
This repository stores the problem as a .py file, so the SQL is kept in the
SQL_SOLUTION string for readability while preserving a valid Python file.
"""
