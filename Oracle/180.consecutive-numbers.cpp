/*
LeetCode 180 is a SQL problem, so there is no meaningful C++ class translation.
This .cpp file documents the canonical answer that the Python placeholder stored.

SQL:
SELECT DISTINCT l1.num AS ConsecutiveNums
FROM Logs l1
JOIN Logs l2 ON l2.id = l1.id + 1
JOIN Logs l3 ON l3.id = l1.id + 2
WHERE l1.num = l2.num AND l2.num = l3.num;

Approach: self-join rows at ids i, i+1, and i+2, then keep triples whose num
values are equal. DISTINCT reports a number once even if it appears in a longer
run.

Data structure note: SQL joins align neighboring rows; no C++ container applies.
With an index on id, the logical scan/join cost is database-dependent, typically
near linear to O(n log n); result space is the number of qualifying numbers.
*/
