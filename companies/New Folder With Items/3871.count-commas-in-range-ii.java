/*
 * @lc app=leetcode id=3871 lang=java
 *
 * [3871] Count Commas in Range II
 *
 * Numbers from 1,000 to 999,999 have one comma, the next three-digit block has
 * two, and so on. Sum whole thousand-based ranges, clipping the final range at n.
 *
 * Time: O(log_1000 n). Space: O(1).
 */

// @lc code=start
class Solution {
    public long countCommas(long n) {
        long answer = 0;
        long start = 1000;
        long commas = 1;

        while (start <= n) {
            long end = start * 1000 - 1;
            long actualEnd = Math.min(n, end);
            answer += (actualEnd - start + 1) * commas;
            start *= 1000;
            commas++;
        }
        return answer;
    }
}
// @lc code=end
