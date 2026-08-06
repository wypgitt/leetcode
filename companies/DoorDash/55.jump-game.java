/**
 * Algorithm:
 * Scan while tracking the farthest reachable index. If the scan reaches an
 * index beyond that reach, progress is impossible. Otherwise update the reach
 * with i + nums[i].
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public boolean canJump(int[] nums) {
        int farthest = 0;
        for (int i = 0; i < nums.length; i++) {
            if (i > farthest) {
                return false;
            }
            farthest = Math.max(farthest, i + nums[i]);
            if (farthest >= nums.length - 1) {
                return true;
            }
        }
        return true;
    }
}

