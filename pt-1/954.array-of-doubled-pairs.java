/*
 * @lc app=leetcode id=954 lang=java
 *
 * [954] Array Of Doubled Pairs
 */

/*
 * --- Interview notes (pair (x, 2x), greedy order by |x|, frequency map, complexity) ---
 *
 * Count frequencies; zeros need even count. Process keys sorted by (abs(x), x); match x with 2x greedily.
 *
 * Time O(n log n), Space O(n).
 *
 * --- end notes ---
 */

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// @lc code=start
class Solution {
    public boolean canReorderDoubled(int[] arr) {
        Map<Integer, Integer> cnt = new HashMap<>();
        for (int x : arr) {
            cnt.merge(x, 1, Integer::sum);
        }
        if (cnt.getOrDefault(0, 0) % 2 != 0) {
            return false;
        }
        List<Integer> keys = new ArrayList<>(cnt.keySet());
        keys.sort(Comparator.comparingInt(Math::abs).thenComparingInt(a -> a));

        for (int x : keys) {
            if (cnt.get(x) == 0) {
                continue;
            }
            long y = 2L * x;
            if (y > Integer.MAX_VALUE || y < Integer.MIN_VALUE) {
                return false;
            }
            int yi = (int) y;
            if (cnt.getOrDefault(yi, 0) < cnt.get(x)) {
                return false;
            }
            cnt.put(yi, cnt.get(yi) - cnt.get(x));
        }
        return true;
    }
}
// @lc code=end
