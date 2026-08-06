/**
 * This LeetCode problem is a database problem, so the executable solution is
 * SQL rather than Java. The original Python file stores the SQL string; this
 * Java translation preserves that solution in a constant.
 *
 * Algorithm:
 * Group by question_id, compute answers divided by shows, and choose the
 * highest rate. Boolean expressions aggregate as 1/0 in MySQL.
 *
 * Database complexity:
 * One grouped scan over SurveyLog, usually improved by indexing question_id.
 */
class Solution {
    static final String SOLUTION_SQL = """
        SELECT question_id AS survey_log
        FROM SurveyLog
        GROUP BY question_id
        ORDER BY SUM(action = 'answer') / SUM(action = 'show') DESC, question_id
        LIMIT 1;
        """;
}

