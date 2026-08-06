package leetcode

// SolutionSQL176 is the SQL answer for LeetCode 176. The source file is Python
// only as a repository container for a SQL problem.
//
// Explanation: MAX(salary) below the global maximum returns the second-highest
// distinct salary. If no such salary exists, SQL MAX over an empty set returns
// NULL, matching the required output.
const SolutionSQL176 = `SELECT MAX(salary) AS SecondHighestSalary
FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);`
