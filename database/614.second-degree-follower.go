package leetcode

// SolutionSQL614 is the SQL answer for LeetCode 614. The source repository
// stored this database problem in a Python file, so the Go translation keeps the
// executable SQL as a raw string constant instead of inventing unrelated Go code.
//
// Explanation: A self join identifies users who are followed and also follow others; COUNT(DISTINCT) avoids duplicate relationship inflation.
// Database complexity is dominated by grouping, sorting, and joins; indexes on
// the join/order/group columns are the relevant optimization.
const SolutionSQL614 = `SELECT f1.followee AS follower, COUNT(DISTINCT f2.followee) AS num
FROM Follow f1
JOIN Follow f2 ON f2.follower = f1.followee
GROUP BY f1.followee
ORDER BY f1.followee;`
