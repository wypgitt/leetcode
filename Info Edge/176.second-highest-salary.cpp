/*
LeetCode 176 is a SQL problem, so there is no meaningful C++ class translation.
This .cpp file documents the canonical answer that the Python placeholder stored.

SQL:
SELECT MAX(salary) AS SecondHighestSalary
FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);

Approach: find the maximum salary strictly below the overall maximum salary.
If no such salary exists, SQL MAX over an empty set returns NULL, which matches
LeetCode's required output.

Data structure note: SQL aggregation performs the scan; no procedural C++ data
structure is involved. Logical complexity is O(n) scan time and O(1) aggregate
space, ignoring database indexing and execution-plan details.
*/
