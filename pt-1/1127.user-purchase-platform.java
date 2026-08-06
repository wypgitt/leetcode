/*
 * LeetCode 1127 — User Purchase Platform  (Database / SQL only)
 *
 * =============================================================================
 * NOTE ON LANGUAGE
 * =============================================================================
 *
 * `1127.user-purchase-platform.py` is empty: this problem is **SQL-only** on
 * LeetCode. Implement in MySQL (or the judge dialect), not Java.
 *
 * =============================================================================
 * PROBLEM SUMMARY
 * =============================================================================
 *
 * Table `Spending(user_id, spend_date, platform, amount)` — spending per user per
 * day per platform (`mobile` / `desktop`). For each `spend_date`, produce rows for
 * platforms `mobile`, `desktop`, and `both` (user spent on both platforms that day),
 * with total amount and total distinct users in each category (see official statement).
 *
 * =============================================================================
 * APPROACH (high level)
 * =============================================================================
 *
 * 1. Per `(spend_date, user_id)`, derive whether that user-day is mobile-only,
 *    desktop-only, or both (e.g. `COUNT(DISTINCT platform)` or conditional agg).
 * 2. Aggregate amount and user counts per `(spend_date, platform_bucket)`.
 * 3. Left join against the Cartesian grid of all dates present × three platform
 *    labels so missing buckets show `0`.
 *
 * =============================================================================
 * REFERENCE SQL SKETCH (complete on official schema — dialect-specific)
 * =============================================================================
 *
 * See community solutions (doocs/leetcode, walkccc) for full MySQL. Pattern:
 *
 * - CTE `user_day` GROUP BY spend_date, user_id → collapse to `mobile` / `desktop` / `both`.
 * - CTE `all_keys` = distinct dates × three platform strings.
 * - LEFT JOIN aggregates onto `all_keys`; `COALESCE` sums and counts.
 *
 * =============================================================================
 */

// @lc code=start
/** Placeholder: submit SQL in LeetCode Database tab. */
class Solution1127SqlOnly {}
// @lc code=end
