/*
 * @lc app=leetcode id=3916 lang=java
 *
 * [3916] Number of Zig Zag Arrays III
 *
 * Block matrix exponentiation on flat arrays; symmetric squaring when base is symmetric.
 */

// @lc code=start
class Solution {
    private static final int MOD = 1_000_000_007;

    public int zigZagArrays(int n, int l, int r) {
        int mod = MOD;
        int m = r - l + 1;

        if (n == 1) {
            return m % mod;
        }
        if (n == 2) {
            return (int) ((long) m * (m - 1) % mod);
        }

        int ex = n - 2;

        int[] ls = buildLFlat(m);
        int[] rs = buildRFlat(m);
        int[] lr = buildMinMatrixFlat(m, mod);
        int[] rl = buildMaxMatrixFlat(m, mod);

        int[] vd = new int[m];
        int[] vu = new int[m];
        for (int j = 0; j < m; j++) {
            vd[j] = j;
            vu[j] = m - 1 - j;
        }

        if (ex % 2 == 0) {
            int k = ex / 2;
            int[] plr = matPowSymmetricBase(lr, m, k, mod);
            int[] prl = matPowSymmetricBase(rl, m, k, mod);
            int[] a = vecMatFlat(vd, plr, m, mod);
            int[] b = vecMatFlat(vu, prl, m, mod);
            return (int) ((sum(a) + sum(b)) % mod);
        } else {
            int k = ex / 2;
            int[] plr = matPowSymmetricBase(lr, m, k, mod);
            int[] prl = matPowSymmetricBase(rl, m, k, mod);
            int[] tmpU = matMulFlat(prl, rs, m, mod);
            int[] tmpD = matMulFlat(plr, ls, m, mod);
            int[] a = vecMatFlat(vu, tmpU, m, mod);
            int[] b = vecMatFlat(vd, tmpD, m, mod);
            return (int) ((sum(a) + sum(b)) % mod);
        }
    }

    private static long sum(int[] a) {
        long s = 0;
        for (int v : a) {
            s += v;
        }
        return s;
    }

    private static int[] buildLFlat(int m) {
        int[] mat = new int[m * m];
        for (int i = 0; i < m; i++) {
            int base = i * m;
            for (int j = 0; j < i; j++) {
                mat[base + j] = 1;
            }
        }
        return mat;
    }

    private static int[] buildRFlat(int m) {
        int[] mat = new int[m * m];
        for (int i = 0; i < m; i++) {
            int base = i * m;
            for (int j = i + 1; j < m; j++) {
                mat[base + j] = 1;
            }
        }
        return mat;
    }

    private static int[] buildMinMatrixFlat(int m, int mod) {
        int[] mat = new int[m * m];
        for (int i = 0; i < m; i++) {
            int row = i * m;
            for (int j = 0; j < m; j++) {
                mat[row + j] = Math.min(i, j) % mod;
            }
        }
        return mat;
    }

    private static int[] buildMaxMatrixFlat(int m, int mod) {
        int[] mat = new int[m * m];
        for (int i = 0; i < m; i++) {
            int row = i * m;
            for (int j = 0; j < m; j++) {
                mat[row + j] = (m - 1 - Math.max(i, j)) % mod;
            }
        }
        return mat;
    }

    private static int[] matPowSymmetricBase(int[] matrix, int m, int p, int mod) {
        int[] r = new int[m * m];
        for (int i = 0; i < m; i++) {
            r[i * m + i] = 1;
        }
        int[] cur = matrix.clone();
        int pow = p;
        while (pow > 0) {
            if ((pow & 1) == 1) {
                r = matMulFlat(r, cur, m, mod);
            }
            cur = symmetricSquareFlat(cur, m, mod);
            pow >>= 1;
        }
        return r;
    }

    private static int[] symmetricSquareFlat(int[] m0, int m, int mod) {
        int[] c = new int[m * m];
        for (int i = 0; i < m; i++) {
            int ib = i * m;
            for (int j = i; j < m; j++) {
                int jb = j * m;
                long s = 0;
                for (int k = 0; k < m; k++) {
                    s += (long) m0[ib + k] * m0[jb + k];
                }
                int v = (int) (s % mod);
                c[ib + j] = v;
                if (i != j) {
                    c[j * m + i] = v;
                }
            }
        }
        return c;
    }

    private static int[] matMulFlat(int[] a, int[] b, int m, int mod) {
        int[] c = new int[m * m];
        for (int i = 0; i < m; i++) {
            int ib = i * m;
            for (int k = 0; k < m; k++) {
                int aik = a[ib + k];
                if (aik == 0) {
                    continue;
                }
                int kb = k * m;
                for (int j = 0; j < m; j++) {
                    c[ib + j] = (int) ((c[ib + j] + (long) aik * b[kb + j]) % mod);
                }
            }
        }
        return c;
    }

    private static int[] vecMatFlat(int[] v, int[] mat, int m, int mod) {
        int[] out = new int[m];
        for (int j = 0; j < m; j++) {
            long s = 0;
            for (int i = 0; i < m; i++) {
                int vi = v[i];
                if (vi != 0) {
                    s = (s + (long) vi * mat[i * m + j]) % mod;
                }
            }
            out[j] = (int) s;
        }
        return out;
    }
}
// @lc code=end
