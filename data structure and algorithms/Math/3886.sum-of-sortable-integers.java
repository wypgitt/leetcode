/*
 * @lc app=leetcode id=3886 lang=java
 *
 * [3886] Sum of Sortable Integers
 *
 * For divisor k of n: each block must multiset-match sorted segment and be a cyclic rotation (KMP).
 */

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

// @lc code=start
class Solution {
    public int sortableIntegers(int[] nums) {
        int n = nums.length;
        int[] s = nums.clone();
        Arrays.sort(s);

        int ans = 0;
        for (int i = 1; i * i <= n; i++) {
            if (n % i == 0) {
                if (ok(nums, s, n, i)) {
                    ans += i;
                }
                int j = n / i;
                if (j != i && ok(nums, s, n, j)) {
                    ans += j;
                }
            }
        }
        return ans;
    }

    private boolean ok(int[] nums, int[] s, int n, int k) {
        for (int i = 0; i < n; i += k) {
            if (!multisetEqual(nums, s, i, k)) {
                return false;
            }
            if (!kmpContains(Arrays.copyOfRange(nums, i, i + k), concatTwice(s, i, k))) {
                return false;
            }
        }
        return true;
    }

    private boolean multisetEqual(int[] nums, int[] s, int start, int k) {
        Map<Integer, Integer> c1 = new HashMap<>();
        Map<Integer, Integer> c2 = new HashMap<>();
        for (int i = 0; i < k; i++) {
            c1.merge(nums[start + i], 1, Integer::sum);
            c2.merge(s[start + i], 1, Integer::sum);
        }
        return c1.equals(c2);
    }

    private int[] concatTwice(int[] s, int start, int k) {
        int[] t = new int[2 * k];
        System.arraycopy(s, start, t, 0, k);
        System.arraycopy(s, start, t, k, k);
        return t;
    }

    private boolean kmpContains(int[] pat, int[] txt) {
        if (pat.length == 0) {
            return true;
        }
        int m = pat.length;
        int ln = txt.length;
        if (m > ln) {
            return false;
        }
        int[] lps = new int[m];
        int len = 0;
        int i = 1;
        while (i < m) {
            if (pat[i] == pat[len]) {
                len++;
                lps[i] = len;
                i++;
            } else if (len > 0) {
                len = lps[len - 1];
            } else {
                lps[i] = 0;
                i++;
            }
        }
        int j = 0;
        i = 0;
        while (i < ln) {
            if (txt[i] == pat[j]) {
                i++;
                j++;
                if (j == m) {
                    return true;
                }
            } else if (j > 0) {
                j = lps[j - 1];
            } else {
                i++;
            }
        }
        return false;
    }
}
// @lc code=end
