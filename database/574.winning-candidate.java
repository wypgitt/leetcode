/**
 * This LeetCode problem is a database problem, so the executable solution is
 * SQL rather than Java. The original Python file stores the SQL string; this
 * Java translation preserves that solution in a constant.
 *
 * Algorithm:
 * Join votes to candidates, group by candidate, and order by descending vote
 * count. The problem guarantees a winner, so LIMIT 1 is enough.
 *
 * Database complexity:
 * Work is dominated by the join and group-by. Indexing Vote(candidateId) and
 * Candidate(id) supports the join efficiently.
 */
class Solution {
    static final String SOLUTION_SQL = """
        SELECT c.name
        FROM Candidate c
        JOIN Vote v ON v.candidateId = c.id
        GROUP BY c.id, c.name
        ORDER BY COUNT(*) DESC
        LIMIT 1;
        """;
}

