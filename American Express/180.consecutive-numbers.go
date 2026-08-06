package leetcode

// SolutionSQL180 is the SQL answer for LeetCode 180. Three self-joined adjacent
// rows detect ids i, i+1, i+2 with equal num; DISTINCT avoids duplicate reporting
// for longer runs.
const SolutionSQL180 = `SELECT DISTINCT l1.num AS ConsecutiveNums
FROM Logs l1
JOIN Logs l2 ON l2.id = l1.id + 1
JOIN Logs l3 ON l3.id = l1.id + 2
WHERE l1.num = l2.num AND l2.num = l3.num;`
