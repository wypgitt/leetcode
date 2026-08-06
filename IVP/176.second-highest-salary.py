"""
LeetCode 176 is a SQL problem. This repository keeps a .py file, so the answer is documented here.

Canonical SQL:
SELECT MAX(salary) AS SecondHighestSalary
FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);

Approach: find the maximum salary strictly below the overall maximum.
Data structure: SQL aggregation handles the scan; no procedural structure is needed.
Interview logic: DISTINCT is unnecessary because MAX below the top salary already ignores duplicate highest salaries. If no second salary exists, MAX over an empty set returns NULL, which is the required output.
Complexity: O(n) logical scan time, O(1) aggregate space.
Tests and edge cases: one employee returns NULL; duplicate highest salaries do not count as second highest; negative or zero salaries compare normally.
"""
