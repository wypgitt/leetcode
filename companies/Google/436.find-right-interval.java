import java.util.*;

/**
 * Algorithm:
 * Sort all interval starts with their original indices. For each interval end,
 * binary-search the first start that is at least that end.
 *
 * Java data structures:
 * A two-column int array stores (start, originalIndex). Arrays.sort with a
 * comparator gives the lower-bound search a compact backing array.
 *
 * Complexity:
 * Time O(n log n), space O(n).
 */
class Solution {
    public int[] findRightInterval(int[][] intervals) {
        int n = intervals.length;
        int[][] starts = new int[n][2];
        for (int i = 0; i < n; i++) {
            starts[i][0] = intervals[i][0];
            starts[i][1] = i;
        }
        Arrays.sort(starts, Comparator.comparingInt(a -> a[0]));

        int[] ans = new int[n];
        for (int i = 0; i < n; i++) {
            int pos = lowerBound(starts, intervals[i][1]);
            ans[i] = pos == n ? -1 : starts[pos][1];
        }
        return ans;
    }

    private int lowerBound(int[][] starts, int target) {
        int lo = 0;
        int hi = starts.length;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (starts[mid][0] < target) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }
}

