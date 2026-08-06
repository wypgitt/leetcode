/**
 * Algorithm:
 * DP over prefixes. dp[j] means s3[0..i+j) can be formed from s1[0..i) and
 * s2[0..j). Each state can come from s1's next char or s2's next char.
 *
 * Java data structures:
 * boolean[] stores one DP row.
 *
 * Complexity:
 * Time O(mn), space O(n).
 */
class Solution {
    public boolean isInterleave(String s1, String s2, String s3) {
        if (s1.length() + s2.length() != s3.length()) {
            return false;
        }
        int n = s2.length();
        boolean[] dp = new boolean[n + 1];
        dp[0] = true;
        for (int i = 0; i <= s1.length(); i++) {
            for (int j = 0; j <= n; j++) {
                if (i == 0 && j == 0) {
                    continue;
                }
                int k = i + j - 1;
                boolean fromS1 = i > 0 && dp[j] && s1.charAt(i - 1) == s3.charAt(k);
                boolean fromS2 = j > 0 && dp[j - 1] && s2.charAt(j - 1) == s3.charAt(k);
                dp[j] = fromS1 || fromS2;
            }
        }
        return dp[n];
    }
}

