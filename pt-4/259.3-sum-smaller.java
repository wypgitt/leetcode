import java.util.*;

/**
 * Algorithm:
 * Sort numbers. For each fixed i, use two pointers. If nums[i]+nums[left]+
 * nums[right] is smaller than target, every index from left+1 through right
 * also works with this left, so add right-left and move left.
 *
 * Complexity:
 * Time O(n^2), space O(1) beyond sorting.
 */
class Solution {
    public int threeSumSmaller(int[] nums, int target) {
        Arrays.sort(nums);
        int count = 0;
        for (int i = 0; i < nums.length - 2; i++) {
            int left = i + 1;
            int right = nums.length - 1;
            while (left < right) {
                if (nums[i] + nums[left] + nums[right] < target) {
                    count += right - left;
                    left++;
                } else {
                    right--;
                }
            }
        }
        return count;
    }
}

