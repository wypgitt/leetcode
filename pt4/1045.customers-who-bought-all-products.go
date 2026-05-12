package main

/*
1045. Customers Who Bought All Products

This is a SQL/database problem rather than a Go runtime problem. The SQL answer
is stored as a Go constant so this directory has a Go file for every problem.
*/
const sqlSolution1045 = `
SELECT
    customer_id
FROM
    Customer
GROUP BY
    customer_id
HAVING
    COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product);
`

/*
Interview Explanation

Core idea:
A customer qualifies if the number of distinct products they bought equals the
total number of products in the Product table.

SQL:
SELECT customer_id
FROM Customer
GROUP BY customer_id
HAVING COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product);

Database data structures and execution intuition:
- GROUP BY customer_id creates one aggregate group per customer.
- COUNT(DISTINCT product_key) counts unique products, so duplicate purchases do
  not inflate the count.
- The scalar subquery counts the required number of products.
- A helpful index is Customer(customer_id, product_key), because it supports
  grouping and distinct product counting.

Correctness:
For each customer, COUNT(DISTINCT product_key) is exactly how many different
products they bought. The subquery is the number of products they must cover.
Equality holds if and only if the customer bought every product.

Complexity:
Conceptually, the database scans Customer, groups by customer_id, and counts
distinct products per group. Product is scanned once for its count. The actual
runtime depends on indexes and the query optimizer.

Edge cases:
- Duplicate purchases are handled by DISTINCT.
- Missing one product filters the customer out.
- If there is one product, every customer who bought it qualifies.
*/
