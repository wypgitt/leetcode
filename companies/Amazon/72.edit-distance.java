/**
 * Algorithm:
 * Dynamic programming on prefixes. dp[j] is the minimum edits from the
 * processed prefix of word1 to word2[0..j). Each cell uses delete, insert, and
 * replace/carry from the previous row.
 *
 * Java data structures:
 * int[] stores one DP row; prevDiag stores the old dp[j - 1].
 *
 * Complexity:
 * Time O(mn), space O(n).
 */
class Solution {
    public int minDistance(String word1, String word2) {
        int m = word1.length();
        int n = word2.length();
        int[] dp = new int[n + 1];
        for (int j = 0; j <= n; j++) {
            dp[j] = j;
        }
        for (int i = 1; i <= m; i++) {
            int prevDiag = dp[0];
            dp[0] = i;
            for (int j = 1; j <= n; j++) {
                int old = dp[j];
                if (word1.charAt(i - 1) == word2.charAt(j - 1)) {
                    dp[j] = prevDiag;
                } else {
                    dp[j] = 1 + Math.min(Math.min(dp[j], dp[j - 1]), prevDiag);
                }
                prevDiag = old;
            }
        }
        return dp[n];
    }
}

