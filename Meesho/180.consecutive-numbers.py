"""
LeetCode 180 is a SQL problem. This repository keeps a .py file, so the answer is documented here.

Canonical SQL:
SELECT DISTINCT l1.num AS ConsecutiveNums
FROM Logs l1
JOIN Logs l2 ON l2.id = l1.id + 1
JOIN Logs l3 ON l3.id = l1.id + 2
WHERE l1.num = l2.num AND l2.num = l3.num;

Approach: self-join three adjacent log rows and keep numbers equal across all three.
Data structure: SQL joins align neighboring ids; DISTINCT removes repeated reporting for longer runs.
Interview logic: three consecutive rows with the same num are detected by ids i, i+1, and i+2.
Complexity: index-assisted joins are effectively O(n log n) or better depending on the database; result space is the number of qualifying numbers.
Tests and edge cases: runs longer than three still appear once; gaps in id do not count; no match returns an empty result.
"""
