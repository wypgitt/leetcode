/*
 * @lc app=leetcode id=3911 lang=java
 *
 * [3911] K-th Smallest Remaining Even Integer in Subarray Queries
 *
 * rem(t) = t/2 - removedEvens(l,r,t); binary search smallest t with rem(t) >= k.
 */

// @lc code=start
class Solution {
    public int[] kthRemainingInteger(int[] nums, int[][] queries) {
        int n = nums.length;
        int[] evenPrefix = new int[n + 1];
        for (int i = 0; i < n; i++) {
            evenPrefix[i + 1] = evenPrefix[i] + ((nums[i] & 1) == 0 ? 1 : 0);
        }

        int[] out = new int[queries.length];
        for (int q = 0; q < queries.length; q++) {
            int l = queries[q][0];
            int r = queries[q][1];
            int k = queries[q][2];
            long hi = 2L * ((long) k + n);
            long lo = 2;
            while (lo < hi) {
                long mid = (lo + hi) >>> 1;
                long rem = mid / 2 - removedEvensUpto(nums, evenPrefix, l, r, mid);
                if (rem >= k) {
                    hi = mid;
                } else {
                    lo = mid + 1;
                }
            }
            out[q] = (int) lo;
        }
        return out;
    }

    private int removedEvensUpto(int[] nums, int[] evenPrefix, int l, int r, long t) {
        int p = upperBound(nums, t) - 1;
        if (p < l) {
            return 0;
        }
        p = Math.min(p, r);
        return evenPrefix[p + 1] - evenPrefix[l];
    }

    /** First index with nums[i] > t. */
    private int upperBound(int[] nums, long t) {
        int lo = 0;
        int hi = nums.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if ((long) nums[mid] <= t) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }
}
// @lc code=end
