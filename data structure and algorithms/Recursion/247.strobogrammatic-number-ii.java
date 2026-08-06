import java.util.*;

/**
 * Algorithm:
 * Recursively build from the center outward using valid mirrored pairs. The
 * outermost layer cannot use 0 unless the total length is 1.
 *
 * Complexity:
 * Output-dependent, O(5^(n/2) * n) time and output space.
 */
class Solution {
    private static final char[][] PAIRS = {
        {'0', '0'}, {'1', '1'}, {'6', '9'}, {'8', '8'}, {'9', '6'}
    };

    public List<String> findStrobogrammatic(int n) {
        return build(n, n);
    }

    private List<String> build(int length, int total) {
        if (length == 0) {
            return new ArrayList<>(Collections.singletonList(""));
        }
        if (length == 1) {
            return new ArrayList<>(Arrays.asList("0", "1", "8"));
        }
        List<String> ans = new ArrayList<>();
        for (String inner : build(length - 2, total)) {
            for (char[] pair : PAIRS) {
                if (length == total && pair[0] == '0') {
                    continue;
                }
                ans.add(pair[0] + inner + pair[1]);
            }
        }
        return ans;
    }
}

