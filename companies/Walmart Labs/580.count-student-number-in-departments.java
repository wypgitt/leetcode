/**
 * This LeetCode problem is a database problem, so the executable solution is
 * SQL rather than Java. The original Python file stores the SQL string; this
 * Java translation preserves that solution in a constant.
 *
 * Algorithm:
 * Start from Department and LEFT JOIN Student so departments with zero
 * students remain. COUNT(student_id) counts only matched student rows.
 *
 * Database complexity:
 * Work is dominated by the join and grouping; Student(dept_id) is the useful
 * join index.
 */
class Solution {
    static final String SOLUTION_SQL = """
        SELECT d.dept_name, COUNT(s.student_id) AS student_number
        FROM Department d
        LEFT JOIN Student s ON s.dept_id = d.dept_id
        GROUP BY d.dept_id, d.dept_name
        ORDER BY student_number DESC, d.dept_name;
        """;
}

