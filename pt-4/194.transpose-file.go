package leetcode

// SolutionAwk194 is the awk answer for LeetCode 194. It stores input fields by
// (column,row) in an associative array, then prints each original column as one
// output row.
const SolutionAwk194 = `awk '{ for (i = 1; i <= NF; i++) a[i, NR] = $i } NF > p { p = NF } END { for (i = 1; i <= p; i++) { line = a[i, 1]; for (j = 2; j <= NR; j++) line = line " " a[i, j]; print line } }' file.txt`
