/**
 * Algorithm:
 * Find the first pivot from the right where nums[i] < nums[i + 1]. Swap it
 * with the smallest larger value in the suffix, then reverse the suffix to make
 * it the smallest possible order. If no pivot exists, reverse the whole array.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public void nextPermutation(int[] nums) {
        int i = nums.length - 2;
        while (i >= 0 && nums[i] >= nums[i + 1]) {
            i--;
        }
        if (i >= 0) {
            int j = nums.length - 1;
            while (nums[j] <= nums[i]) {
                j--;
            }
            swap(nums, i, j);
        }
        reverse(nums, i + 1, nums.length - 1);
    }

    private void reverse(int[] nums, int left, int right) {
        while (left < right) {
            swap(nums, left++, right--);
        }
    }

    private void swap(int[] nums, int i, int j) {
        int tmp = nums[i];
        nums[i] = nums[j];
        nums[j] = tmp;
    }
}

