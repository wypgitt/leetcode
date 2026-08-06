/*
 * @lc app=leetcode id=397 lang=java
 *
 * [397] Integer Replacement
 *
 * Greedy bit rule: even numbers must divide by two. For odd numbers, decrement
 * when n == 3 or the low two bits are 01; otherwise increment to create more
 * trailing zeroes and enable repeated division by two.
 *
 * Java note: use long internally so n = 2^31 - 1 can safely increment.
 *
 * Time: O(log n). Space: O(1).
 */

// @lc code=start
class Solution {
    public int integerReplacement(int n) {
        long value = n;
        int steps = 0;

        while (value != 1) {
            if ((value & 1) == 0) {
                value >>= 1;
            } else if (value == 3 || (value & 3) == 1) {
                value--;
            } else {
                value++;
            }
            steps++;
        }
        return steps;
    }
}
// @lc code=end
