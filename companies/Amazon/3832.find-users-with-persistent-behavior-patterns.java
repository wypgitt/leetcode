/*
 * LeetCode 3832 - Find Users With Persistent Behavior Patterns (Database / SQL)
 *
 * =============================================================================
 * NOTE ON LANGUAGE
 * =============================================================================
 *
 * The companion Python file is empty. This is a database problem; LeetCode
 * expects SQL in the Database tab, not a Java class submission.
 *
 * =============================================================================
 * REFERENCE MYSQL
 * =============================================================================
 *
 * WITH daily_counts AS (
 *     SELECT user_id, action_date, action,
 *            COUNT(*) OVER (PARTITION BY user_id, action_date) AS cnt
 *     FROM activity
 * ),
 * filtered_activity AS (
 *     SELECT user_id, action_date, action
 *     FROM daily_counts
 *     WHERE cnt = 1
 * ),
 * streak_groups AS (
 *     SELECT user_id, action, action_date,
 *            DATE_SUB(action_date, INTERVAL ROW_NUMBER() OVER (
 *                PARTITION BY user_id, action
 *                ORDER BY action_date
 *            ) DAY) AS streak_key
 *     FROM filtered_activity
 * ),
 * streak_summary AS (
 *     SELECT user_id, action,
 *            COUNT(*) AS streak_length,
 *            MIN(action_date) AS start_date,
 *            MAX(action_date) AS end_date,
 *            ROW_NUMBER() OVER (
 *                PARTITION BY user_id
 *                ORDER BY COUNT(*) DESC, MIN(action_date) ASC, action ASC
 *            ) AS rn
 *     FROM streak_groups
 *     GROUP BY user_id, action, streak_key
 *     HAVING COUNT(*) >= 5
 * ),
 * SELECT user_id, action, streak_length, start_date, end_date
 * FROM streak_summary
 * WHERE rn = 1
 * ORDER BY streak_length DESC, user_id ASC;
 *
 * =============================================================================
 * ALGORITHM
 * =============================================================================
 *
 * First remove user dates that have multiple actions. Consecutive daily streaks
 * are grouped by the classic date-minus-row-number key per (user_id, action).
 * After grouping, keep streaks of length at least 5, rank each user's qualifying
 * streaks by longest length, and return the top row.
 *
 * SQL complexity is dominated by the window sort:
 * O(N log N) time and O(N) working space in a typical execution plan.
 */

// @lc code=start
/** Placeholder: LeetCode expects SQL for problem 3832, not Java. */
class Solution3832SqlOnly {}
// @lc code=end
