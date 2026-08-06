import java.util.*;

/**
 * Algorithm:
 * Scan every length-10 substring. The first time a window repeats, add it to
 * the repeated set.
 *
 * Java data structures:
 * HashSet<String> stores seen windows and repeated windows.
 *
 * Complexity:
 * Time O(n) windows with constant length substring cost 10; space O(n).
 */
class Solution {
    public List<String> findRepeatedDnaSequences(String s) {
        Set<String> seen = new HashSet<>();
        Set<String> repeated = new HashSet<>();
        for (int i = 0; i + 10 <= s.length(); i++) {
            String window = s.substring(i, i + 10);
            if (!seen.add(window)) {
                repeated.add(window);
            }
        }
        return new ArrayList<>(repeated);
    }
}

