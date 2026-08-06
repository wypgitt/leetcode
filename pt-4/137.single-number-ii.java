/**
 * Algorithm:
 * Track bits seen once and twice with two masks. When a bit has appeared three
 * times, it is removed from both masks. The remaining once mask is the answer.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int singleNumber(int[] nums) {
        int ones = 0;
        int twos = 0;
        for (int num : nums) {
            ones = (ones ^ num) & ~twos;
            twos = (twos ^ num) & ~ones;
        }
        return ones;
    }
}

