import java.util.*;

/**
 * Algorithm:
 * The sum of absolute distances is minimized at a median. Sort, choose the
 * middle value, and sum distances to it.
 *
 * Complexity:
 * Time O(n log n), space O(1) beyond the in-place sort.
 */
class Solution {
    public int minMoves2(int[] nums) {
        Arrays.sort(nums);
        int median = nums[nums.length / 2];
        int ans = 0;
        for (int x : nums) {
            ans += Math.abs(x - median);
        }
        return ans;
    }
}

