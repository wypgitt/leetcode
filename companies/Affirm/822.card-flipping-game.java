import java.util.*;

/**
 * Algorithm:
 * Any number appearing on both sides of the same card is impossible to hide
 * from all fronts, so it is banned. The answer is the smallest number appearing
 * anywhere that is not banned.
 *
 * Java data structures:
 * HashSet stores banned values.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public int flipgame(int[] fronts, int[] backs) {
        Set<Integer> banned = new HashSet<>();
        for (int i = 0; i < fronts.length; i++) {
            if (fronts[i] == backs[i]) {
                banned.add(fronts[i]);
            }
        }
        int ans = Integer.MAX_VALUE;
        for (int x : fronts) {
            if (!banned.contains(x)) {
                ans = Math.min(ans, x);
            }
        }
        for (int x : backs) {
            if (!banned.contains(x)) {
                ans = Math.min(ans, x);
            }
        }
        return ans == Integer.MAX_VALUE ? 0 : ans;
    }
}

