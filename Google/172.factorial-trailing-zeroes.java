/**
 * Algorithm:
 * Trailing zeroes come from factors of 10, and factors of 5 are scarcer than
 * factors of 2. Count multiples of 5, 25, 125, and so on.
 *
 * Complexity:
 * Time O(log_5 n), space O(1).
 */
class Solution {
    public int trailingZeroes(int n) {
        int count = 0;
        while (n != 0) {
            n /= 5;
            count += n;
        }
        return count;
    }
}
