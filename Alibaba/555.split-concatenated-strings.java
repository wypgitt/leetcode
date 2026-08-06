import java.util.*;

/**
 * Algorithm:
 * For every string, choose the lexicographically larger orientation for all
 * non-starting pieces. Then try each string as the split piece in both
 * orientations and every cut position, keeping the largest rotation.
 *
 * Java data structures:
 * StringBuilder is used for reversal and candidate construction.
 *
 * Complexity:
 * If total length is L, trying every cut builds O(L) candidates of length L,
 * so time O(L^2) and space O(L).
 */
class Solution {
    public String splitLoopedString(String[] strs) {
        int n = strs.length;
        String[] parts = new String[n];
        for (int i = 0; i < n; i++) {
            String rev = reverse(strs[i]);
            parts[i] = strs[i].compareTo(rev) >= 0 ? strs[i] : rev;
        }

        String best = "";
        for (int i = 0; i < n; i++) {
            StringBuilder middleBuilder = new StringBuilder();
            for (int j = i + 1; j < n; j++) {
                middleBuilder.append(parts[j]);
            }
            for (int j = 0; j < i; j++) {
                middleBuilder.append(parts[j]);
            }
            String middle = middleBuilder.toString();

            String original = strs[i];
            String reversed = reverse(original);
            String[] sources = {original, reversed};
            for (String source : sources) {
                for (int cut = 0; cut < source.length(); cut++) {
                    String candidate = source.substring(cut) + middle + source.substring(0, cut);
                    if (candidate.compareTo(best) > 0) {
                        best = candidate;
                    }
                }
            }
        }
        return best;
    }

    private String reverse(String s) {
        return new StringBuilder(s).reverse().toString();
    }
}

