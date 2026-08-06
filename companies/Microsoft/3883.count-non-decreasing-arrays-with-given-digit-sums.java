/*
 * @lc app=leetcode id=3883 lang=java
 *
 * [3883] Count Non Decreasing Arrays With Given Digit Sums
 *
 * DP: prev[v] ways ending with value v; transition prefix sum over u <= v. Buckets by digit sum 0..5000.
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    private static final int MOD = 1_000_000_007;
    private static final int MAXV = 5000;
    private static final List<Integer>[] BY_SUM = buildBySum();

    @SuppressWarnings("unchecked")
    private static List<Integer>[] buildBySum() {
        List<Integer>[] buckets = new List[51];
        for (int i = 0; i <= 50; i++) {
            buckets[i] = new ArrayList<>();
        }
        for (int x = 0; x <= MAXV; x++) {
            buckets[digitSum(x)].add(x);
        }
        return buckets;
    }

    private static int digitSum(int x) {
        int s = 0;
        while (x > 0) {
            s += x % 10;
            x /= 10;
        }
        return s;
    }

    public int countArrays(int[] digitSum) {
        for (int s : digitSum) {
            if (s > 50 || BY_SUM[s].isEmpty()) {
                return 0;
            }
        }

        int[] prev = new int[MAXV + 1];
        for (int v : BY_SUM[digitSum[0]]) {
            prev[v] = 1;
        }

        for (int i = 1; i < digitSum.length; i++) {
            int running = 0;
            int[] pref = new int[MAXV + 1];
            for (int t = 0; t <= MAXV; t++) {
                running = (running + prev[t]) % MOD;
                pref[t] = running;
            }
            int[] cur = new int[MAXV + 1];
            for (int v : BY_SUM[digitSum[i]]) {
                cur[v] = pref[v];
            }
            prev = cur;
        }

        int ans = 0;
        for (int v : prev) {
            ans = (ans + v) % MOD;
        }
        return ans;
    }
}
// @lc code=end
