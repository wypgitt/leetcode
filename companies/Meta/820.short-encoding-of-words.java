import java.util.*;

/**
 * Algorithm:
 * A word needs no separate encoding if it is a suffix of another word. Put all
 * words in a set, remove every proper suffix of every word, then sum the
 * remaining word lengths plus one '#'.
 *
 * Java data structures:
 * HashSet deduplicates words and supports O(1) average suffix removal.
 *
 * Complexity:
 * Counting substring creation, worst-case time O(sum len(word)^2), space O(L).
 */
class Solution {
    public int minimumLengthEncoding(String[] words) {
        Set<String> useful = new HashSet<>(Arrays.asList(words));
        for (String word : words) {
            for (int i = 1; i < word.length(); i++) {
                useful.remove(word.substring(i));
            }
        }
        int ans = 0;
        for (String word : useful) {
            ans += word.length() + 1;
        }
        return ans;
    }
}

