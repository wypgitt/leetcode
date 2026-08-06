/*
LeetCode 192 is a shell problem, so there is no meaningful C++ class translation.
This .cpp file documents the canonical shell pipeline from the Python placeholder.

Shell:
tr -s ' ' '\n' < words.txt | sort | uniq -c | sort -nr | awk '{print $2, $1}'

Approach: split words onto separate lines, sort them so equal words are adjacent,
count adjacent equal lines with uniq -c, sort by descending count, then print word
followed by count.

Data structure note: Unix text streams plus sort/uniq perform grouping and
counting. Complexity is dominated by sorting: O(n log n) time and O(n) external
storage depending on the implementation.
*/
