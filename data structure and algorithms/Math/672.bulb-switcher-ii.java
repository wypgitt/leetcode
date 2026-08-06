import java.util.*;

/**
 * Algorithm:
 * Only the first six bulbs can distinguish final states because all button
 * effects repeat with period 6. Enumerate the 16 subsets of four button types
 * and keep those whose button count has the same parity as presses and does not
 * exceed presses.
 *
 * Java data structures:
 * HashSet<String> stores unique state patterns.
 *
 * Complexity:
 * Constant time and space: at most 16 masks and 6 bulbs.
 */
class Solution {
    public int flipLights(int n, int presses) {
        n = Math.min(n, 6);
        Set<String> seen = new HashSet<>();
        for (int mask = 0; mask < 16; mask++) {
            int bits = Integer.bitCount(mask);
            if (bits > presses || (presses - bits) % 2 != 0) {
                continue;
            }
            StringBuilder state = new StringBuilder();
            for (int i = 1; i <= n; i++) {
                int on = 1;
                if ((mask & 1) != 0) {
                    on ^= 1;
                }
                if ((mask & 2) != 0 && i % 2 == 0) {
                    on ^= 1;
                }
                if ((mask & 4) != 0 && i % 2 == 1) {
                    on ^= 1;
                }
                if ((mask & 8) != 0 && i % 3 == 1) {
                    on ^= 1;
                }
                state.append(on);
            }
            seen.add(state.toString());
        }
        return seen.size();
    }
}

