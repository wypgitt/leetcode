package leetcode

// SolutionSQL534 is the SQL answer for LeetCode 534. The source repository
// stored this database problem in a Python file, so the Go translation keeps the
// executable SQL as a raw string constant instead of inventing unrelated Go code.
//
// Explanation: Window running sum partitioned by player and ordered by event_date keeps one row per activity and accumulates games through that date.
// Database complexity is dominated by grouping, sorting, and joins; indexes on
// the join/order/group columns are the relevant optimization.
const SolutionSQL534 = `SELECT
    player_id,
    event_date,
    SUM(games_played) OVER (
        PARTITION BY player_id
        ORDER BY event_date
    ) AS games_played_so_far
FROM Activity;`
