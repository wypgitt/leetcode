/**
 * This LeetCode problem is a database problem, so the executable solution is
 * SQL rather than Java. The original Python file stores the SQL string; this
 * Java translation preserves that solution in a constant.
 *
 * Algorithm:
 * Find each player's first login, left join an Activity row exactly one day
 * later, and average whether that joined row exists. The LEFT JOIN keeps
 * players who did not return, contributing 0 to the average.
 *
 * Database complexity:
 * Grouping by player_id and probing (player_id, event_date) dominate. An index
 * on those two columns helps both the MIN step and the join.
 */
class Solution {
    static final String SOLUTION_SQL = """
        WITH first_login AS (
            SELECT player_id, MIN(event_date) AS first_date
            FROM Activity
            GROUP BY player_id
        )
        SELECT ROUND(AVG(a.event_date IS NOT NULL), 2) AS fraction
        FROM first_login f
        LEFT JOIN Activity a
            ON a.player_id = f.player_id
           AND a.event_date = DATE_ADD(f.first_date, INTERVAL 1 DAY);
        """;
}

