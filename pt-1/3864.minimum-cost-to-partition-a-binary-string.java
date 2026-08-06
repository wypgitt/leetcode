/*
 * @lc app=leetcode id=3864 lang=java
 *
 * [3864] Minimum Cost to Partition a Binary String
 *
 * Dyadic divide-and-conquer: cost unsplit or split at midpoint when length even. Prefix sums for
 * ones count; segment cost flat if no ones else L * ones * encCost.
 */

// @lc code=start
class Solution {
    public long minCost(String s, int encCost, int flatCost) {
        int n = s.length();
        int[] pre = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            pre[i] = pre[i - 1] + (s.charAt(i - 1) - '0');
        }
        return dfs(0, n, pre, encCost, flatCost);
    }

    private long dfs(int l, int r, int[] pre, int encCost, int flatCost) {
        int x = pre[r] - pre[l];
        int len = r - l;
        long res = x == 0 ? flatCost : (long) len * x * encCost;
        if (len % 2 == 0) {
            int m = (l + r) / 2;
            res = Math.min(res, dfs(l, m, pre, encCost, flatCost) + dfs(m, r, pre, encCost, flatCost));
        }
        return res;
    }
}
// @lc code=end
