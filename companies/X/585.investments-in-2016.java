/**
 * This LeetCode problem is a database problem, so the executable solution is
 * SQL rather than Java. The original Python file stores the SQL string; this
 * Java translation preserves that solution in a constant.
 *
 * Algorithm:
 * Keep rows whose tiv_2015 value appears more than once, while their (lat, lon)
 * pair appears exactly once. The two grouped subqueries express those
 * independent filters before summing tiv_2016.
 *
 * Database complexity:
 * Dominated by two group-by operations and a filtered scan. Indexes on
 * tiv_2015 and (lat, lon) help.
 */
class Solution {
    static final String SOLUTION_SQL = """
        SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
        FROM Insurance
        WHERE tiv_2015 IN (
            SELECT tiv_2015
            FROM Insurance
            GROUP BY tiv_2015
            HAVING COUNT(*) > 1
        )
        AND (lat, lon) IN (
            SELECT lat, lon
            FROM Insurance
            GROUP BY lat, lon
            HAVING COUNT(*) = 1
        );
        """;
}

