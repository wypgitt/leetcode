/*
 * LeetCode 1375 - Number of Times Binary String Is Prefix-Aligned
 */
class Solution {
    public int numTimesAllBlue(int[] flips) {
        int maxPosition = 0;
        int moments = 0;

        for (int step = 1; step <= flips.length; step++) {
            maxPosition = Math.max(maxPosition, flips[step - 1]);
            if (maxPosition == step) {
                moments++;
            }
        }

        return moments;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * After `step` flips, exactly `step` positions are on. The prefix is all blue
 * exactly when the largest flipped position is `step`; then the flipped set is
 * positions 1 through step.
 *
 * Java data structures:
 * Only two integers are needed: the maximum flipped position so far and the
 * answer count.
 *
 * Edge cases:
 * - If the first flip is 1, the first moment counts.
 * - A large position flipped early blocks counting until all earlier positions
 *   have appeared.
 * - The final step always counts because all positions are flipped.
 *
 * Complexity:
 * Time O(n).
 * Space O(1).
 */
