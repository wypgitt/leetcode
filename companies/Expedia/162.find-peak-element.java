/**
 * Algorithm:
 * Binary search on slope. If nums[mid] < nums[mid + 1], a peak exists to the
 * right; otherwise a peak exists at mid or to the left.
 *
 * Complexity:
 * Time O(log n), space O(1).
 */
class Solution {
    public int findPeakElement(int[] nums) {
        int left = 0;
        int right = nums.length - 1;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] < nums[mid + 1]) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return left;
    }
}

