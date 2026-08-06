/**
 * Algorithm:
 * Binary search compares mid with right. If nums[mid] > nums[right], the
 * minimum is to the right of mid; otherwise it is at mid or to the left.
 *
 * Complexity:
 * Time O(log n), space O(1).
 */
class Solution {
    public int findMin(int[] nums) {
        int left = 0;
        int right = nums.length - 1;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] > nums[right]) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return nums[left];
    }
}

