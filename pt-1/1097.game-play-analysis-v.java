/*
 * LeetCode 1097 — Game Play Analysis V  (Database / SQL only)
 *
 * =============================================================================
 * NOTE ON LANGUAGE
 * =============================================================================
 *
 * The companion file `1097.game-play-analysis-v.py` is empty because this
 * problem is judged in **MySQL** (or another SQL dialect), not Python or Java.
 * Submit the query in LeetCode's **Database** environment.
 *
 * =============================================================================
 * PROBLEM SUMMARY (interview-style)
 * =============================================================================
 *
 * Table `Activity(player_id, device_id, event_date, games_played)`.
 * `(player_id, event_date)` is unique. Install date = first `event_date` per player.
 *
 * For each install date `x`, report:
 *   - how many players installed on `x`;
 *   - **day-one retention**: among those installers, fraction who logged in again on
 *     the calendar day immediately after `x`, rounded to 2 decimals.
 *
 * =============================================================================
 * WHY SET / WINDOW SQL
 * =============================================================================
 *
 * Per player we need install date (aggregate min date or window `MIN OVER`).
 * Then join each row to see if there exists `event_date = install_dt + 1 day`.
 * Retention = (# players with next-day login) / (# installers).
 *
 * =============================================================================
 * REFERENCE MYSQL (submit this on LeetCode — not compiled Java)
 * =============================================================================
 *
 * WITH T AS (
 *     SELECT player_id, event_date,
 *            MIN(event_date) OVER (PARTITION BY player_id) AS install_dt
 *     FROM Activity
 * )
 * SELECT install_dt,
 *        COUNT(DISTINCT player_id) AS installs,
 *        ROUND(SUM(DATEDIFF(event_date, install_dt) = 1) / COUNT(DISTINCT player_id), 2)
 *            AS Day1_retention
 * FROM T
 * GROUP BY install_dt;
 *
 * (Dialect note: `DATEDIFF(event_date, install_dt) = 1` flags exactly the next day.)
 *
 * =============================================================================
 * COMPLEXITY (SQL execution plan level)
 * =============================================================================
 *
 * Typically O(N log N) sort or hash for grouping; single pass over Activity per CTE.
 *
 * =============================================================================
 */

// @lc code=start
/** Placeholder: LeetCode expects MySQL in the Database tab, not Java. */
class Solution1097SqlOnly {}
// @lc code=end
