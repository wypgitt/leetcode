/**
 * This LeetCode problem is a database problem, so the executable solution is
 * SQL rather than Java. The original Python file stores the SQL string; this
 * Java translation preserves that solution in a constant.
 *
 * Algorithm:
 * Use a window running sum partitioned by player_id and ordered by event_date.
 * This keeps one output row per original activity row while accumulating games
 * played through that date.
 *
 * Database complexity:
 * Work is dominated by sorting/ordering Activity by (player_id, event_date).
 * An index on those columns is the main practical optimization.
 */
class Solution {
    static final String SOLUTION_SQL = """
        SELECT
            player_id,
            event_date,
            SUM(games_played) OVER (
                PARTITION BY player_id
                ORDER BY event_date
            ) AS games_played_so_far
        FROM Activity;
        """;
}

