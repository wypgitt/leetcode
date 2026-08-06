/*
 * @lc app=leetcode id=483 lang=java
 *
 * [483] Smallest Good Base
 *
 * A good base k represents n as 1 + k + ... + k^power. Try the largest possible
 * power first; the first matching base is smallest. Binary search base and stop
 * geometric summation once it exceeds n.
 *
 * Java note: long is enough for LeetCode's n <= 10^18; overflow is avoided by
 * stopping multiplication when the running sum exceeds the limit.
 *
 * Time: O(log^3 n). Space: O(1).
 */

// @lc code=start
class Solution {
    public String smallestGoodBase(String n) {
        long number = Long.parseLong(n);
        int maxPower = 63 - Long.numberOfLeadingZeros(number) - 1;

        for (int power = maxPower; power > 1; power--) {
            long left = 2;
            long right = number - 1;
            while (left <= right) {
                long mid = left + ((right - left) >>> 1);
                long sum = geometricSum(mid, power, number);
                if (sum == number) {
                    return Long.toString(mid);
                }
                if (sum < number) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }
        return Long.toString(number - 1);
    }

    private long geometricSum(long base, int power, long limit) {
        long total = 1;
        long term = 1;
        for (int i = 0; i < power; i++) {
            if (term > limit / base) {
                return limit + 1;
            }
            term *= base;
            total += term;
            if (total > limit) {
                return total;
            }
        }
        return total;
    }
}
// @lc code=end
