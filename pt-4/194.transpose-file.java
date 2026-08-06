/**
 * LeetCode 194 is a shell problem, so there is no Java runtime API. This Java
 * file preserves the canonical awk answer and the algorithm explanation.
 *
 * Algorithm:
 * Store each input field by (column,row), then print columns as output rows.
 * The awk associative array acts as a sparse matrix.
 *
 * Complexity:
 * Time O(r*c), space O(r*c).
 */
class Solution {
    static final String SOLUTION_AWK = """
        awk '{ for (i = 1; i <= NF; i++) a[i, NR] = $i } NF > p { p = NF } END { for (i = 1; i <= p; i++) { line = a[i, 1]; for (j = 2; j <= NR; j++) line = line " " a[i, j]; print line } }' file.txt
        """;
}

