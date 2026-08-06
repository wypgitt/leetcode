/**
 * Algorithm:
 * Greedy BFS by ranges. currentEnd is the farthest index reachable with the
 * current number of jumps; farthest is the best reach found while scanning that
 * range. When i reaches currentEnd, take one jump and extend the range.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int jump(int[] nums) {
        int jumps = 0;
        int currentEnd = 0;
        int farthest = 0;
        for (int i = 0; i < nums.length - 1; i++) {
            farthest = Math.max(farthest, i + nums[i]);
            if (i == currentEnd) {
                jumps++;
                currentEnd = farthest;
            }
        }
        return jumps;
    }
}

