/*
 * @lc app=leetcode id=3906 lang=java
 *
 * [3906] Count Good Integers on a Grid Path
 *
 * Digit DP: 16-digit bound, path cells enforce monotone chain in visit order.
 */

// @lc code=start
class Solution {
    private boolean[] key;
    private char[] bound;
    private long[][][] memo;
    private boolean[][][] done;

    public int countGoodIntegersOnPath(int l, int r, String directions) {
        key = new boolean[16];
        int row = 0;
        int col = 0;
        key[0] = true;
        for (int i = 0; i < directions.length(); i++) {
            char c = directions.charAt(i);
            if (c == 'D') {
                row++;
            } else {
                col++;
            }
            key[row * 4 + col] = true;
        }
        return (int) (calc(r) - calc(l - 1));
    }

    private long calc(int x) {
        if (x < 0) {
            return 0;
        }
        bound = zfill16(x);
        memo = new long[17][11][2];
        done = new boolean[17][11][2];
        return dfs(0, 0, 1);
    }

    private char[] zfill16(int x) {
        String r = Integer.toString(x);
        if (r.length() >= 16) {
            return r.toCharArray();
        }
        char[] s = new char[16];
        int pad = 16 - r.length();
        for (int i = 0; i < pad; i++) {
            s[i] = '0';
        }
        for (int i = 0; i < r.length(); i++) {
            s[pad + i] = r.charAt(i);
        }
        return s;
    }

    private long dfs(int pos, int last, int lim) {
        if (done[pos][last][lim]) {
            return memo[pos][last][lim];
        }
        if (pos == 16) {
            done[pos][last][lim] = true;
            memo[pos][last][lim] = 1;
            return 1;
        }
        long res = 0;
        int start = key[pos] ? last : 0;
        int end = lim == 1 ? (bound[pos] - '0') : 9;
        for (int i = start; i <= end; i++) {
            int nlast = key[pos] ? i : last;
            int nlim = (lim == 1 && i == end) ? 1 : 0;
            res += dfs(pos + 1, nlast, nlim);
        }
        done[pos][last][lim] = true;
        memo[pos][last][lim] = res;
        return res;
    }
}
// @lc code=end
