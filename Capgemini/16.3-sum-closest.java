import java.util.*;

/**
 * Algorithm:
 * Sort, fix one number, and use two pointers for the remaining pair. Keep the
 * sum with the smallest absolute difference from target.
 *
 * Complexity:
 * Time O(n^2), extra space O(1) after in-place sort.
 */
class Solution {
    public int threeSumClosest(int[] nums, int target) {
        Arrays.sort(nums);
        int closest = nums[0] + nums[1] + nums[2];
        for (int i = 0; i < nums.length - 2; i++) {
            int left = i + 1;
            int right = nums.length - 1;
            while (left < right) {
                int total = nums[i] + nums[left] + nums[right];
                if (Math.abs(total - target) < Math.abs(closest - target)) {
                    closest = total;
                }
                if (total == target) {
                    return target;
                }
                if (total < target) {
                    left++;
                } else {
                    right--;
                }
            }
        }
        return closest;
    }
}

