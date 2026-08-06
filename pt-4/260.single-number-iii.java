/**
 * Algorithm:
 * XOR of all numbers equals a ^ b for the two unique numbers. Pick the lowest
 * set bit in that XOR to partition numbers into two groups; duplicates remain
 * together and cancel, leaving one unique value per group.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int[] singleNumber(int[] nums) {
        int xorAll = 0;
        for (int num : nums) {
            xorAll ^= num;
        }
        int mask = xorAll & -xorAll;
        int a = 0;
        for (int num : nums) {
            if ((num & mask) != 0) {
                a ^= num;
            }
        }
        return new int[] {a, xorAll ^ a};
    }
}

