/**
 * This LeetCode problem is a database problem, so the executable solution is
 * SQL rather than Java. The original Python file stores the SQL string; this
 * Java translation preserves that solution in a constant.
 *
 * Algorithm:
 * Self-join Follow where a followed user is also a follower. Group that middle
 * user and count distinct people they follow.
 *
 * Database complexity:
 * Dominated by the self-join and grouping. Indexes on follower and followee
 * are useful.
 */
class Solution {
    static final String SOLUTION_SQL = """
        SELECT f1.followee AS follower, COUNT(DISTINCT f2.followee) AS num
        FROM Follow f1
        JOIN Follow f2 ON f2.follower = f1.followee
        GROUP BY f1.followee
        ORDER BY f1.followee;
        """;
}

