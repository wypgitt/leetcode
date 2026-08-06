/*
 * @lc app=leetcode id=923 lang=java
 *
 * [923] 3Sum With Multiplicity
 */

/*
 * --- Interview notes (combinatorics, multiset, bounded domain, modular arithmetic) ---
 *
 * Problem
 * Count index triples i < j < k with arr[i] + arr[j] + arr[k] = target. Values repeat — multiset triples (x, y, z) with x ≤ y ≤ z,
 * combine counts via combinatorics. Return count mod 10^9+7.
 *
 * Why frequencies matter (constraints arr[i] in [0, 100])
 * At most ~101 distinct values — enumerate value triples a ≤ b ≤ c with a+b+c=target on distinct keys.
 * Time O(U²) with U ≤ 101.
 *
 * Case analysis — ways to choose three indices
 * • a < b < c — cnt[a]*cnt[b]*cnt[c]
 * • a = b < c — C(cnt[a],2)*cnt[c]
 * • a < b = c — cnt[a]*C(cnt[b],2)
 * • a = b = c — C(cnt[a],3)
 *
 * --- end notes ---
 */

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// @lc code=start
class Solution {
    private static final int MOD = 1_000_000_007;

    public int threeSumMulti(int[] arr, int target) {
        Map<Integer, Integer> cntMap = new HashMap<>();
        for (int x : arr) {
            cntMap.merge(x, 1, Integer::sum);
        }
        List<Integer> keys = new ArrayList<>(cntMap.keySet());
        Collections.sort(keys);

        long ans = 0;
        for (int i = 0; i < keys.size(); i++) {
            for (int j = i; j < keys.size(); j++) {
                int a = keys.get(i);
                int b = keys.get(j);
                int c = target - a - b;
                if (c < b) {
                    continue;
                }
                if (!cntMap.containsKey(c)) {
                    continue;
                }

                long ca = cntMap.get(a);
                long cb = cntMap.get(b);
                long cc = cntMap.get(c);

                if (a == b && b == c) {
                    ans = (ans + ca * (ca - 1) * (ca - 2) / 6) % MOD;
                } else if (a == b) {
                    ans = (ans + ca * (ca - 1) / 2 * cc) % MOD;
                } else if (b == c) {
                    ans = (ans + ca * cb * (cb - 1) / 2) % MOD;
                } else {
                    ans = (ans + ca * cb * cc) % MOD;
                }
            }
        }
        return (int) ans;
    }
}
// @lc code=end
