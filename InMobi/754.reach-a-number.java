/**
 * Algorithm:
 * Move in the positive direction until the triangular sum reaches target and
 * the difference has even parity. Flipping the sign of one step changes the
 * final position by twice that step, so only parity matters after overshooting.
 *
 * Complexity:
 * Time O(sqrt(target)), space O(1).
 */
class Solution {
    public int reachNumber(int target) {
        target = Math.abs(target);
        int step = 0;
        int total = 0;
        while (total < target || (total - target) % 2 != 0) {
            step++;
            total += step;
        }
        return step;
    }
}

