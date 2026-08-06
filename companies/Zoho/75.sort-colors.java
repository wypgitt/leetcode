/**
 * Algorithm:
 * Dutch national flag partitioning. [0, low) are 0s, [low, mid) are 1s,
 * (high, end] are 2s, and mid scans the unknown region.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public void sortColors(int[] nums) {
        int low = 0;
        int mid = 0;
        int high = nums.length - 1;
        while (mid <= high) {
            if (nums[mid] == 0) {
                swap(nums, low++, mid++);
            } else if (nums[mid] == 2) {
                swap(nums, mid, high--);
            } else {
                mid++;
            }
        }
    }

    private void swap(int[] nums, int i, int j) {
        int tmp = nums[i];
        nums[i] = nums[j];
        nums[j] = tmp;
    }
}

