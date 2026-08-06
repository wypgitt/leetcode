/**
 * Algorithm:
 * Use lower_bound for the first occurrence and upper_bound for the index after
 * the last occurrence. This avoids target + 1 overflow for Integer.MAX_VALUE.
 *
 * Java data structures:
 * The helper performs binary search directly on the int array.
 *
 * Complexity:
 * Time O(log n), space O(1).
 */
class Solution {
    public int[] searchRange(int[] nums, int target) {
        int first = lowerBound(nums, target);
        if (first == nums.length || nums[first] != target) {
            return new int[] {-1, -1};
        }
        return new int[] {first, upperBound(nums, target) - 1};
    }

    private int lowerBound(int[] nums, int value) {
        int left = 0;
        int right = nums.length;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] < value) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return left;
    }

    private int upperBound(int[] nums, int value) {
        int left = 0;
        int right = nums.length;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] <= value) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return left;
    }
}
