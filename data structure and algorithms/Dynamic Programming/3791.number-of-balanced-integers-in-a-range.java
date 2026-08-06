/*
 * @lc app=leetcode id=3791 lang=java
 *
 * [3791] Number of Balanced Integers in a Range
 *
 * Count balanced values up to a bound with digit DP, then subtract. The state is
 * index, alternating digit-sum difference, and tight flag. Fixed shorter
 * lengths are counted by using an all-9 bound of that length.
 *
 * Java note: HashMap memoization is used only for non-tight states hidden
 * behind the compact "index#diff#tight" key.
 *
 * Time: O(d^2 * 10) per bound for d digits. Space: O(d^2).
 */

import java.util.HashMap;
import java.util.Map;

// @lc code=start
class Solution {
    public long countBalanced(long low, long high) {
        return countUpTo(high) - countUpTo(low - 1);
    }

    private long countUpTo(long limit) {
        if (limit < 10) {
            return 0;
        }
        int[] digits = digits(limit);
        long total = 0;
        for (int length = 2; length < digits.length; length++) {
            int[] bound = new int[length];
            for (int i = 0; i < length; i++) {
                bound[i] = 9;
            }
            total += countFixedLength(bound);
        }
        total += countFixedLength(digits);
        return total;
    }

    private long countFixedLength(int[] boundDigits) {
        return dfs(boundDigits, 0, 0, true, new HashMap<>());
    }

    private long dfs(int[] digits, int index, int diff, boolean tight, Map<String, Long> memo) {
        if (index == digits.length) {
            return diff == 0 ? 1 : 0;
        }
        String key = index + "#" + diff + "#" + tight;
        if (memo.containsKey(key)) {
            return memo.get(key);
        }

        int upper = tight ? digits[index] : 9;
        int lower = index == 0 ? 1 : 0;
        long total = 0;
        for (int digit = lower; digit <= upper; digit++) {
            int nextDiff = (index & 1) == 0 ? diff + digit : diff - digit;
            total += dfs(digits, index + 1, nextDiff, tight && digit == upper, memo);
        }
        memo.put(key, total);
        return total;
    }

    private int[] digits(long value) {
        char[] chars = Long.toString(value).toCharArray();
        int[] out = new int[chars.length];
        for (int i = 0; i < chars.length; i++) {
            out[i] = chars[i] - '0';
        }
        return out;
    }
}
// @lc code=end
