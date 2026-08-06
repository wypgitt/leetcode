import java.util.*;

/**
 * Algorithm:
 * Store all values in a set. Only start counting from numbers that have no
 * predecessor num - 1; then walk forward through the consecutive run.
 *
 * Java data structures:
 * HashSet<Integer> gives O(1) average membership checks.
 *
 * Complexity:
 * Time O(n) average, space O(n).
 */
class Solution {
    public int longestConsecutive(int[] nums) {
        Set<Integer> values = new HashSet<>();
        for (int num : nums) {
            values.add(num);
        }
        int best = 0;
        for (int num : values) {
            if (values.contains(num - 1)) {
                continue;
            }
            int length = 1;
            while (values.contains(num + length)) {
                length++;
            }
            best = Math.max(best, length);
        }
        return best;
    }
}

