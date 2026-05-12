import java.util.*;

class Solution {
    public int longestCommonSubsequence(String text1, String text2) {
        if (text2.length() > text1.length()) {
            String temp = text1;
            text1 = text2;
            text2 = temp;
        }

        int[] dp = new int[text2.length() + 1];
        for (int i = 0; i < text1.length(); i++) {
            int previousDiagonal = 0;
            for (int j = 1; j <= text2.length(); j++) {
                int saved = dp[j];
                if (text1.charAt(i) == text2.charAt(j - 1)) {
                    dp[j] = previousDiagonal + 1;
                } else {
                    dp[j] = Math.max(dp[j], dp[j - 1]);
                }
                previousDiagonal = saved;
            }
        }

        return dp[text2.length()];
    }
}

