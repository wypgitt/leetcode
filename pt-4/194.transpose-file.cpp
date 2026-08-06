/*
LeetCode 194 is a shell problem, so there is no meaningful C++ class translation.
This .cpp file documents the canonical awk solution from the Python placeholder.

Awk:
awk '{ for (i = 1; i <= NF; i++) a[i, NR] = $i } NF > p { p = NF } END { for (i = 1; i <= p; i++) { line = a[i, 1]; for (j = 2; j <= NR; j++) line = line " " a[i, j]; print line } }' file.txt

Approach: store each field by (column,row), then emit each original column as an
output row. This is matrix transposition over whitespace-separated fields.

Data structure note: awk's associative array indexed by column and row acts as a
sparse matrix. Complexity is O(r*c) time and O(r*c) space.
*/
