/*
 * @lc app=leetcode id=583 lang=java
 *
 * [583] Delete Operation for Two Strings
 *
 * Only deletions are allowed, so the final equal string must be a common
 * subsequence. Keep the longest common subsequence; delete everything else.
 * A one-dimensional rolling DP computes LCS length.
 *
 * Time: O(|word1| * |word2|). Space: O(min lengths).
 */

// @lc code=start
class Solution {
    public int minDistance(String word1, String word2) {
        if (word2.length() > word1.length()) {
            String tmp = word1;
            word1 = word2;
            word2 = tmp;
        }

        int[] dp = new int[word2.length() + 1];
        for (int i = 0; i < word1.length(); i++) {
            int previousDiagonal = 0;
            for (int j = 1; j <= word2.length(); j++) {
                int previousRowSameColumn = dp[j];
                if (word1.charAt(i) == word2.charAt(j - 1)) {
                    dp[j] = previousDiagonal + 1;
                } else {
                    dp[j] = Math.max(dp[j], dp[j - 1]);
                }
                previousDiagonal = previousRowSameColumn;
            }
        }

        int lcs = dp[word2.length()];
        return word1.length() + word2.length() - 2 * lcs;
    }
}
// @lc code=end
