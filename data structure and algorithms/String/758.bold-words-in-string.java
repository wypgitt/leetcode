import java.util.*;

/**
 * Algorithm:
 * Mark every character covered by any word occurrence, then rebuild the string
 * while opening and closing bold tags around contiguous marked ranges.
 *
 * Java data structures:
 * boolean[] stores the coverage marks.
 *
 * Complexity:
 * Let W be the total work of repeated indexOf searches and marking. Rebuilding
 * is O(|s|), and space is O(|s|).
 */
class Solution {
    public String boldWords(String[] words, String s) {
        boolean[] bold = new boolean[s.length()];
        for (String word : words) {
            int start = s.indexOf(word);
            while (start != -1) {
                for (int i = start; i < start + word.length(); i++) {
                    bold[i] = true;
                }
                start = s.indexOf(word, start + 1);
            }
        }

        StringBuilder ans = new StringBuilder();
        int i = 0;
        while (i < s.length()) {
            if (!bold[i]) {
                ans.append(s.charAt(i++));
            } else {
                ans.append("<b>");
                while (i < s.length() && bold[i]) {
                    ans.append(s.charAt(i++));
                }
                ans.append("</b>");
            }
        }
        return ans.toString();
    }
}

