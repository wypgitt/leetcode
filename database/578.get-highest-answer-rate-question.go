package leetcode

// SolutionSQL578 is the SQL answer for LeetCode 578. The source repository
// stored this database problem in a Python file, so the Go translation keeps the
// executable SQL as a raw string constant instead of inventing unrelated Go code.
//
// Explanation: Aggregate answers divided by shows per question and order by rate, then question id for deterministic ties.
// Database complexity is dominated by grouping, sorting, and joins; indexes on
// the join/order/group columns are the relevant optimization.
const SolutionSQL578 = `SELECT question_id AS survey_log
FROM SurveyLog
GROUP BY question_id
ORDER BY SUM(action = 'answer') / SUM(action = 'show') DESC, question_id
LIMIT 1;`
