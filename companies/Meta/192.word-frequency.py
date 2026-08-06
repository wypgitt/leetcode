"""
LeetCode 192 is a shell problem. This repository keeps a .py file, so the shell answer is documented here.

Canonical shell pipeline:
tr -s ' ' '
' < words.txt | sort | uniq -c | sort -nr | awk '{print $2, $1}'

Approach: split words onto separate lines, sort them, count identical lines, then sort by descending frequency.
Data structure: Unix text streams plus sort/uniq provide the grouping and counting behavior.
Interview logic: uniq -c only counts adjacent equal records, so sorting before uniq is required. The final awk prints word then count in LeetCode's expected order.
Complexity: dominated by sort, O(n log n) time and O(n) external storage depending on implementation.
Tests and edge cases: repeated spaces are squeezed by tr -s; one word appears with count 1; ties may be output in any order accepted by the original problem constraints.
"""
