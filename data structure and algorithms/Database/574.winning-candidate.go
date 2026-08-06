package leetcode

// SolutionSQL574 is the SQL answer for LeetCode 574. The source repository
// stored this database problem in a Python file, so the Go translation keeps the
// executable SQL as a raw string constant instead of inventing unrelated Go code.
//
// Explanation: Join votes to candidates, group by candidate, and select the largest vote count.
// Database complexity is dominated by grouping, sorting, and joins; indexes on
// the join/order/group columns are the relevant optimization.
const SolutionSQL574 = `SELECT c.name
FROM Candidate c
JOIN Vote v ON v.candidateId = c.id
GROUP BY c.id, c.name
ORDER BY COUNT(*) DESC
LIMIT 1;`
