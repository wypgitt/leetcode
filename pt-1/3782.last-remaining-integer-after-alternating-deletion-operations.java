/*
 * @lc app=leetcode id=3782 lang=java
 *
 * [3782] Last Remaining Integer After Alternating Deletion Operations
 *
 * The remaining values are always an arithmetic progression. Track first,
 * step, count, and direction instead of materializing the list. A right-to-left
 * pass with even count removes the current first value, so first shifts by step.
 *
 * Time: O(log n). Space: O(1).
 */

// @lc code=start
class Solution {
    public long lastInteger(long n) {
        long first = 1;
        long step = 1;
        long count = n;
        boolean deleteFromLeft = true;

        while (count > 1) {
            if (!deleteFromLeft && count % 2 == 0) {
                first += step;
            }
            count = (count + 1) / 2;
            step *= 2;
            deleteFromLeft = !deleteFromLeft;
        }
        return first;
    }
}
// @lc code=end
