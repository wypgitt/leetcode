/**
 * Algorithm:
 * Reverse the whole array, reverse the first k elements, then reverse the
 * remaining elements. This rotates right by k in place.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public void rotate(int[] nums, int k) {
        int n = nums.length;
        k %= n;
        reverse(nums, 0, n - 1);
        reverse(nums, 0, k - 1);
        reverse(nums, k, n - 1);
    }

    private void reverse(int[] nums, int left, int right) {
        while (left < right) {
            int tmp = nums[left];
            nums[left++] = nums[right];
            nums[right--] = tmp;
        }
    }
}

