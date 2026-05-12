/*
 * 1045. Customers Who Bought All Products
 *
 * This is a SQL/database LeetCode problem, not a Java runtime problem. The SQL
 * answer is stored here so every pt4 problem has a Java file, as requested.
 */
class Solution {
    static final String SQL_SOLUTION =
        "SELECT customer_id\n" +
        "FROM Customer\n" +
        "GROUP BY customer_id\n" +
        "HAVING COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product);";
}

/*
Interview Explanation

Core idea:
A customer qualifies when the number of distinct products they bought equals
the total number of products in the Product table.

SQL answer:
SELECT customer_id
FROM Customer
GROUP BY customer_id
HAVING COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product);

Database data structures and execution intuition:
- GROUP BY customer_id forms one aggregate group per customer.
- COUNT(DISTINCT product_key) counts unique products, so repeated purchases do
  not inflate the result.
- The scalar subquery counts how many products must be covered.
- A useful physical index is Customer(customer_id, product_key), which helps
  grouping and distinct counting.

Correctness:
For each customer group, COUNT(DISTINCT product_key) is exactly how many
different products that customer bought. The subquery is exactly the number of
products available. Equality holds if and only if the customer bought every
product.

Complexity:
Conceptually, the database scans Customer, groups rows by customer_id, and
counts distinct product keys per group. Product is scanned once for the total
count. Actual runtime depends on indexes and the database optimizer.

Edge cases:
- Duplicate purchases are handled by DISTINCT.
- Missing one product filters the customer out.
- With one product, every customer who bought it qualifies.
*/
