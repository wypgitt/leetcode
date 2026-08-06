package leetcode

// SolutionSQL550 is the SQL answer for LeetCode 550. The source repository
// stored this database problem in a Python file, so the Go translation keeps the
// executable SQL as a raw string constant instead of inventing unrelated Go code.
//
// Explanation: Find each player first login, left join to the next day, and average the boolean match; missing matches contribute zero.
// Database complexity is dominated by grouping, sorting, and joins; indexes on
// the join/order/group columns are the relevant optimization.
const SolutionSQL550 = `WITH first_login AS (
    SELECT player_id, MIN(event_date) AS first_date
    FROM Activity
    GROUP BY player_id
)
SELECT ROUND(AVG(a.event_date IS NOT NULL), 2) AS fraction
FROM first_login f
LEFT JOIN Activity a
    ON a.player_id = f.player_id
   AND a.event_date = DATE_ADD(f.first_date, INTERVAL 1 DAY);`
