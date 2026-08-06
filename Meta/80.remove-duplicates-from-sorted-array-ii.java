/**
 * Algorithm:
 * Keep a write pointer. A value is accepted if fewer than two values have been
 * written, or if it differs from the value two positions before write.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int removeDuplicates(int[] nums) {
        int write = 0;
        for (int num : nums) {
            if (write < 2 || num != nums[write - 2]) {
                nums[write++] = num;
            }
        }
        return write;
    }
}

