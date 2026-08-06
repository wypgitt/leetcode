/*
 * @lc app=leetcode id=3901 lang=java
 *
 * [3901] Good Subsequence Queries
 *
 * Segment tree for range GCD on stored values (non-multiples as 0). Updates + gcd checks per query.
 */

// @lc code=start
class Solution {
    private int[] t;
    private int n;

    public int countGoodSubseq(int[] nums, int p, int[][] queries) {
        n = nums.length;
        t = new int[4 * n + 4];
        int cnt = 0;
        for (int i = 0; i < n; i++) {
            if (nums[i] % p == 0) {
                modify(1, 1, n, i + 1, nums[i]);
                cnt++;
            }
        }

        int ans = 0;
        for (int[] q : queries) {
            int idx = q[0];
            int val = q[1];

            if (nums[idx] % p == 0) {
                modify(1, 1, n, idx + 1, 0);
                cnt--;
            }
            if (val % p == 0) {
                modify(1, 1, n, idx + 1, val);
                cnt++;
            }
            nums[idx] = val;

            if (t[1] != p) {
                continue;
            }
            if (cnt < n || n > 6) {
                ans++;
                continue;
            }

            boolean ok = false;
            for (int i = 1; i <= n; i++) {
                int leftG = query(1, 1, n, 1, i - 1);
                int rightG = query(1, 1, n, i + 1, n);
                if (gcd(leftG, rightG) == p) {
                    ok = true;
                    break;
                }
            }
            if (ok) {
                ans++;
            }
        }
        return ans;
    }

    private void modify(int u, int l, int r, int x, int v) {
        if (l == r) {
            t[u] = v;
            return;
        }
        int m = (l + r) >> 1;
        if (x <= m) {
            modify(u << 1, l, m, x, v);
        } else {
            modify(u << 1 | 1, m + 1, r, x, v);
        }
        t[u] = gcd(t[u << 1], t[u << 1 | 1]);
    }

    private int query(int u, int l, int r, int L, int R) {
        if (L > R) {
            return 0;
        }
        if (l >= L && r <= R) {
            return t[u];
        }
        int m = (l + r) >> 1;
        if (R <= m) {
            return query(u << 1, l, m, L, R);
        }
        if (L > m) {
            return query(u << 1 | 1, m + 1, r, L, R);
        }
        return gcd(query(u << 1, l, m, L, m), query(u << 1 | 1, m + 1, r, m + 1, R));
    }

    private static int gcd(int a, int b) {
        while (b != 0) {
            int tmp = a % b;
            a = b;
            b = tmp;
        }
        return Math.abs(a);
    }
}
// @lc code=end
