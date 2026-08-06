/*
 * @lc app=leetcode id=3915 lang=java
 *
 * [3915] Maximum Sum of Alternating Subsequence With Distance At Least K
 *
 * high/low DP with two max segment trees on compressed coordinates; insert index i-k at step i.
 */

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

// @lc code=start
class SegTreeMax {
    private final int n;
    private final int size;
    private final long neg;
    private final long[] t;

    SegTreeMax(int n, long neg) {
        this.n = n;
        this.neg = neg;
        int s = 1;
        while (s < n) {
            s <<= 1;
        }
        this.size = s;
        t = new long[2 * s];
        Arrays.fill(t, neg);
    }

    void update(int i, long val) {
        i += size;
        t[i] = Math.max(t[i], val);
        i >>= 1;
        while (i > 0) {
            t[i] = Math.max(t[2 * i], t[2 * i + 1]);
            i >>= 1;
        }
   
    }

    long query(int l, int r) {
        if (l > r) {
            return neg;
        }
        l += size;
        r += size;
        long res = neg;
        while (l <= r) {
            if ((l & 1) == 1) {
                res = Math.max(res, t[l++]);
            }
            if ((r & 1) == 0) {
                res = Math.max(res, t[r--]);
            }
            l >>= 1;
            r >>= 1;
        }
        return res;
    }
}

class Solution {
    public long maxAlternatingSum(int[] nums, int k) {
        int n = nums.length;
        int[] vals = nums.clone();
        Arrays.sort(vals);
        int m = 0;
        for (int i = 0; i < n; i++) {
            if (i == 0 || vals[i] != vals[i - 1]) {
                m++;
            }
        }
        int[] uniq = new int[m];
        m = 0;
        for (int i = 0; i < n; i++) {
            if (i == 0 || vals[i] != vals[i - 1]) {
                uniq[m++] = vals[i];
            }
        }

        Map<Integer, Integer> coord = new HashMap<>();
        for (int i = 0; i < uniq.length; i++) {
            coord.put(uniq[i], i);
        }

        final long neg = (long) -1e18;
        SegTreeMax stLow = new SegTreeMax(m, neg);
        SegTreeMax stHigh = new SegTreeMax(m, neg);

        long[] high = new long[n];
        long[] low = new long[n];
        long ans = neg;

        for (int i = 0; i < n; i++) {
            if (i >= k) {
                int p = i - k;
                int pos = coord.get(nums[p]);
                stLow.update(pos, low[p]);
                stHigh.update(pos, high[p]);
            }

            int pos = coord.get(nums[i]);
            long ml = stLow.query(0, pos - 1);
            long mh = stHigh.query(pos + 1, m - 1);

            high[i] = nums[i];
            low[i] = nums[i];
            if (ml != neg) {
                high[i] = Math.max(high[i], ml + nums[i]);
            }
            if (mh != neg) {
                low[i] = Math.max(low[i], mh + nums[i]);
            }

            ans = Math.max(ans, Math.max(high[i], low[i]));
        }
        return ans;
    }
}
// @lc code=end
