/**
 * LeetCode 176 is a SQL problem, so there is no Java runtime API. This Java
 * file preserves the canonical SQL answer and the algorithm explanation.
 *
 * Algorithm:
 * Find the maximum salary strictly below the overall maximum. MAX over an
 * empty set returns NULL, which is the required result when no second salary
 * exists.
 *
 * Complexity:
 * Logical scan time O(n), aggregate space O(1).
 */
class Solution {
    static final String SOLUTION_SQL = """
        SELECT MAX(salary) AS SecondHighestSalary
        FROM Employee
        WHERE salary < (SELECT MAX(salary) FROM Employee);
        """;
}

