/*
 * LeetCode 569 - Median Employee Salary (Database / SQL)
 *
 * =============================================================================
 * NOTE ON LANGUAGE
 * =============================================================================
 *
 * The companion Python file is empty because this is a SQL database problem.
 * LeetCode expects a query in the Database tab, not Java.
 *
 * =============================================================================
 * REFERENCE MYSQL
 * =============================================================================
 *
 * WITH ranked AS (
 *     SELECT id, company, salary,
 *            ROW_NUMBER() OVER (PARTITION BY company ORDER BY salary, id) AS rn,
 *            COUNT(*) OVER (PARTITION BY company) AS cnt
 *     FROM Employee
 * )
 * SELECT id, company, salary
 * FROM ranked
 * WHERE rn IN ((cnt + 1) DIV 2, (cnt + 2) DIV 2);
 *
 * =============================================================================
 * ALGORITHM
 * =============================================================================
 *
 * Rank salaries within each company. For an odd company size, both median
 * positions collapse to the same row. For an even company size, the two middle
 * rows are returned.
 *
 * SQL complexity is typically O(N log N) due to partition ordering and O(N)
 * working space for window execution.
 */

// @lc code=start
/** Placeholder: LeetCode expects SQL for problem 569, not Java. */
class Solution569SqlOnly {}
// @lc code=end
