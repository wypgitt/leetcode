/**
 * Algorithm:
 * Two pointers on the sorted array. If the sum is too small, move left up; if
 * too large, move right down.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int[] twoSum(int[] numbers, int target) {
        int left = 0;
        int right = numbers.length - 1;
        while (left < right) {
            int total = numbers[left] + numbers[right];
            if (total == target) {
                return new int[] {left + 1, right + 1};
            }
            if (total < target) {
                left++;
            } else {
                right--;
            }
        }
        return new int[0];
    }
}

