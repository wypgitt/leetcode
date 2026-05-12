/*
 * LeetCode 1310 - XOR Queries of a Subarray
 */
class Solution {
    public int[] xorQueries(int[] arr, int[][] queries) {
        int[] prefix = new int[arr.length + 1];
        for (int i = 0; i < arr.length; i++) {
            prefix[i + 1] = prefix[i] ^ arr[i];
        }

        int[] answer = new int[queries.length];
        for (int i = 0; i < queries.length; i++) {
            int left = queries[i][0];
            int right = queries[i][1];
            answer[i] = prefix[right + 1] ^ prefix[left];
        }

        return answer;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * XOR has a cancellation property: x ^ x = 0. If `prefix[i]` is the XOR of
 * arr[0..i-1], then arr[left..right] is `prefix[right + 1] ^ prefix[left]`.
 *
 * Java data structures:
 * An `int[]` prefix array is compact and fast. The extra leading 0 removes the
 * need for a special case when a query starts at index 0.
 *
 * Edge cases:
 * - Query [0, r] works because prefix[0] is 0.
 * - Query [i, i] returns the single element.
 * - Repeated values are handled naturally by XOR cancellation.
 *
 * Complexity:
 * Time O(n + q), where q is the number of queries.
 * Space O(n), excluding the output array.
 */
