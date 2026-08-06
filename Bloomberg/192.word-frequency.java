/**
 * LeetCode 192 is a shell problem, so there is no Java runtime API. This Java
 * file preserves the canonical shell pipeline and the algorithm explanation.
 *
 * Algorithm:
 * Split words to one per line, sort, count adjacent equal words with uniq -c,
 * sort by descending count, then print word and count.
 *
 * Complexity:
 * Dominated by sort: O(n log n) time and O(n) external storage depending on the
 * implementation.
 */
class Solution {
    static final String SOLUTION_SHELL = """
        tr -s ' ' '\\n' < words.txt | sort | uniq -c | sort -nr | awk '{print $2, $1}'
        """;
}

