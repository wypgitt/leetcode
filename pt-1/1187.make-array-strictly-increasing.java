/*
 * @lc app=leetcode id=1187 lang=java
 *
 * [1187] Make Array Strictly Increasing
 */

// @lc code=start
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

class Solution {
    private static int upperBound(int[] a, int x) {
        int lo = 0;
        int hi = a.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] <= x) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }

    private static int upperBoundForPrev(int[] u, long prev) {
        if (prev <= Integer.MIN_VALUE) {
            return 0;
        }
        if (prev >= Integer.MAX_VALUE) {
            return u.length;
        }
        return upperBound(u, (int) prev);
    }

    public int makeArrayIncreasing(int[] arr1, int[] arr2) {
        int[] u = Arrays.stream(arr2).distinct().sorted().toArray();
        long negInf = -1_000_000_000_000_000_000L;
        Map<Long, Integer> dp = new HashMap<>();
        dp.put(negInf, 0);

        for (int a : arr1) {
            Map<Long, Integer> nxt = new HashMap<>();
            for (Map.Entry<Long, Integer> e : dp.entrySet()) {
                long prev = e.getKey();
                int cost = e.getValue();
                if (prev < a) {
                    nxt.merge((long) a, cost, Math::min);
                }
                int j = upperBoundForPrev(u, prev);
                if (j < u.length) {
                    int x = u[j];
                    int nc = cost + 1;
                    nxt.merge((long) x, nc, Math::min);
                }
            }
            dp = nxt;
            if (dp.isEmpty()) {
                return -1;
            }
        }
        int ans = Integer.MAX_VALUE;
        for (int c : dp.values()) {
            ans = Math.min(ans, c);
        }
        return ans;
    }
}
// @lc code=end
