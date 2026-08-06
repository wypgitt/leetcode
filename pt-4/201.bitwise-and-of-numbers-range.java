/**
 * Algorithm:
 * The range AND keeps only the common binary prefix of left and right. Shift
 * both right until they match, count shifts, then shift the prefix back.
 *
 * Complexity:
 * Time O(32), space O(1).
 */
class Solution {
    public int rangeBitwiseAnd(int left, int right) {
        int shift = 0;
        while (left < right) {
            left >>= 1;
            right >>= 1;
            shift++;
        }
        return left << shift;
    }
}

