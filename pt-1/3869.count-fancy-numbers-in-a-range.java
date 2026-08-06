/*
 * @lc app=leetcode id=3869 lang=java
 *
 * [3869] Count Fancy Numbers in a Range
 *
 * Fancy: strictly monotone decimal string OR digit sum satisfies check(s). F(r)-F(l-1) with digit
 * DP on bound string; fresh memo per bound.
 */

// @lc code=start
class Solution {
    public int countFancy(int l, int r) {
        return calc(r) - calc(l - 1);
    }

    private boolean check(int s) {
        if (s < 100) {
            return s % 11 != 0;
        }
        int a = (s / 10) % 10;
        int b = s % 10;
        return 1 < a && a < b;
    }

    private int dfs(
            int pos,
            int s,
            int prev,
            int st,
            int lim,
            char[] num,
            int[][][][][] memo) {
        if (pos >= num.length) {
            if (st != 3) {
                return 1;
            }
            return check(s) ? 1 : 0;
        }
        if (memo[pos][s][prev][st][lim] != -1) {
            return memo[pos][s][prev][st][lim];
        }
        int up = lim == 1 ? (num[pos] - '0') : 9;
        int res = 0;
        for (int i = 0; i <= up; i++) {
            int nxtSt = st;
            if (st == 0) {
                if (prev == 0) {
                    nxtSt = 0;
                } else if (i > prev) {
                    nxtSt = 1;
                } else if (i < prev) {
                    nxtSt = 2;
                } else {
                    nxtSt = 3;
                }
            } else if (st == 1) {
                nxtSt = i > prev ? 1 : 3;
            } else if (st == 2) {
                nxtSt = i < prev ? 2 : 3;
            } else {
                nxtSt = 3;
            }
            int nlim = (lim == 1 && i == up) ? 1 : 0;
            res += dfs(pos + 1, s + i, i, nxtSt, nlim, num, memo);
        }
        memo[pos][s][prev][st][lim] = res;
        return res;
    }

    private int calc(int x) {
        if (x < 0) {
            return 0;
        }
        String str = Integer.toString(x);
        char[] num = str.toCharArray();
        int d = num.length;
        int maxS = d * 9 + 1;
        int[][][][][] memo = new int[d][maxS][11][4][2];
        for (int i = 0; i < d; i++) {
            for (int j = 0; j < maxS; j++) {
                for (int p = 0; p < 11; p++) {
                    for (int t = 0; t < 4; t++) {
                        memo[i][j][p][t][0] = -1;
                        memo[i][j][p][t][1] = -1;
                    }
                }
            }
        }
        return dfs(0, 0, 0, 0, 1, num, memo);
    }
}
// @lc code=end
