/*
 * @lc app=leetcode id=2719 lang=java
 *
 * [2719] Count of Integers
 */

// @lc code=start
class Solution {
    private static final int MOD = 1_000_000_007;

    public int count(String num1, String num2, int min_sum, int max_sum) {
        int sub = countLeq(subOne(num1), min_sum, max_sum);
        int upto = countLeq(num2, min_sum, max_sum);
        return (upto - sub + MOD) % MOD;
    }

    private static String subOne(String s) {
        char[] t = s.toCharArray();
        int i = t.length - 1;
        while (i >= 0) {
            if (t[i] != '0') {
                t[i]--;
                break;
            }
            t[i] = '9';
            i--;
        }
        String r = new String(t).replaceFirst("^0+(?!$)", "");
        return r.isEmpty() ? "0" : r;
    }

    private int countLeq(String num, int min_sum, int max_sum) {
        int len = num.length();
        int maxS = Math.min(max_sum, len * 9);
        int[][][] memo = new int[len][maxS + 1][2];
        for (int i = 0; i < len; i++) {
            for (int j = 0; j <= maxS; j++) {
                java.util.Arrays.fill(memo[i][j], -1);
            }
        }
        return dfs(num, 0, 0, true, min_sum, max_sum, memo);
    }

    private int dfs(
            String num,
            int pos,
            int sum,
            boolean limit,
            int min_sum,
            int max_sum,
            int[][][] memo) {
        if (sum > max_sum) {
            return 0;
        }
        int lim = limit ? 1 : 0;
        if (memo[pos][sum][lim] != -1) {
            return memo[pos][sum][lim];
        }
        if (pos >= num.length()) {
            return (min_sum <= sum && sum <= max_sum) ? 1 : 0;
        }
        int up = limit ? (num.charAt(pos) - '0') : 9;
        int tot = 0;
        for (int d = 0; d <= up; d++) {
            if (sum + d > max_sum) {
                continue;
            }
            tot = (tot + dfs(num, pos + 1, sum + d, limit && d == up, min_sum, max_sum, memo)) % MOD;
        }
        return memo[pos][sum][lim] = tot;
    }
}
// @lc code=end
