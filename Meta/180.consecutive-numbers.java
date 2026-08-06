/**
 * LeetCode 180 is a SQL problem, so there is no Java runtime API. This Java
 * file preserves the canonical SQL answer and the algorithm explanation.
 *
 * Algorithm:
 * Self-join three adjacent log rows and keep rows where all three nums are
 * equal. DISTINCT reports each qualifying number once even for longer runs.
 *
 * Complexity:
 * Index-assisted joins are typically O(n log n) or better depending on the
 * database engine; output space is the number of qualifying nums.
 */
class Solution {
    static final String SOLUTION_SQL = """
        SELECT DISTINCT l1.num AS ConsecutiveNums
        FROM Logs l1
        JOIN Logs l2 ON l2.id = l1.id + 1
        JOIN Logs l3 ON l3.id = l1.id + 2
        WHERE l1.num = l2.num AND l2.num = l3.num;
        """;
}

