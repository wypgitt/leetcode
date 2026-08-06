import java.util.*;

/**
 * Algorithm:
 * DP over prefixes. dp[i] is true if s[0..i) can be segmented. Only try word
 * lengths present in the dictionary.
 *
 * Java data structures:
 * HashSet<String> gives O(1) average dictionary checks; HashSet<Integer> stores
 * candidate lengths.
 *
 * Complexity:
 * Time O(n * L * substring cost), where L is number of distinct lengths. Space
 * O(n + dictionary).
 */
class Solution {
    public boolean wordBreak(String s, List<String> wordDict) {
        Set<String> words = new HashSet<>(wordDict);
        Set<Integer> lengths = new HashSet<>();
        for (String word : words) {
            lengths.add(word.length());
        }
        boolean[] dp = new boolean[s.length() + 1];
        dp[0] = true;
        for (int i = 1; i <= s.length(); i++) {
            for (int length : lengths) {
                if (i >= length && dp[i - length] && words.contains(s.substring(i - length, i))) {
                    dp[i] = true;
                    break;
                }
            }
        }
        return dp[s.length()];
    }
}

