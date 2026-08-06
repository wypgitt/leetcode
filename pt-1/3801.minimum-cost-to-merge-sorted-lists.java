/*
 * @lc app=leetcode id=3801 lang=java
 *
 * [3801] Minimum Cost to Merge Sorted Lists
 *
 * Bitmask DP over subsets of lists. Precompute each subset's total length and
 * merged median; then split every subset into two parts and pay both subcosts
 * plus merge length and median difference.
 *
 * Java note: subset medians are found by binary search over all distinct values;
 * Arrays.binarySearch-style upper bounds count elements <= candidate in each
 * sorted source list.
 *
 * Time: O(3^m + 2^m * m * VlogV) for m lists. Space: O(2^m).
 */

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

// @lc code=start
class Solution {
    public long minMergeCost(int[][] lists) {
        int m = lists.length;
        int maskCount = 1 << m;
        int[] lengths = new int[maskCount];
        int[][] members = new int[maskCount][];

        members[0] = new int[0];
        for (int mask = 1; mask < maskCount; mask++) {
            int bit = mask & -mask;
            int index = Integer.numberOfTrailingZeros(bit);
            int prev = mask ^ bit;
            lengths[mask] = lengths[prev] + lists[index].length;
            members[mask] = Arrays.copyOf(members[prev], members[prev].length + 1);
            members[mask][members[mask].length - 1] = index;
        }

        int[] values = distinctValues(lists);
        int[][] countLeq = new int[m][values.length];
        for (int i = 0; i < m; i++) {
            for (int v = 0; v < values.length; v++) {
                countLeq[i][v] = upperBound(lists[i], values[v]);
            }
        }

        int[] medians = new int[maskCount];
        for (int mask = 1; mask < maskCount; mask++) {
            medians[mask] = subsetMedian(mask, lengths, members, values, countLeq);
        }

        long inf = Long.MAX_VALUE / 4;
        long[] dp = new long[maskCount];
        Arrays.fill(dp, inf);
        for (int i = 0; i < m; i++) {
            dp[1 << i] = 0;
        }

        for (int mask = 1; mask < maskCount; mask++) {
            if ((mask & (mask - 1)) == 0) {
                continue;
            }
            long best = inf;
            int sub = (mask - 1) & mask;
            while (sub > 0) {
                int other = mask ^ sub;
                if (sub < other) {
                    long candidate = dp[sub] + dp[other] + lengths[mask]
                            + Math.abs((long) medians[sub] - medians[other]);
                    best = Math.min(best, candidate);
                }
                sub = (sub - 1) & mask;
            }
            dp[mask] = best;
        }
        return dp[maskCount - 1];
    }

    private int subsetMedian(int mask, int[] lengths, int[][] members, int[] values, int[][] countLeq) {
        int target = (lengths[mask] - 1) / 2 + 1;
        int left = 0;
        int right = values.length - 1;
        while (left < right) {
            int mid = (left + right) >>> 1;
            int count = 0;
            for (int listIndex : members[mask]) {
                count += countLeq[listIndex][mid];
            }
            if (count >= target) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return values[left];
    }

    private int[] distinctValues(int[][] lists) {
        List<Integer> all = new ArrayList<>();
        for (int[] list : lists) {
            for (int value : list) {
                all.add(value);
            }
        }
        int[] arr = new int[all.size()];
        for (int i = 0; i < all.size(); i++) {
            arr[i] = all.get(i);
        }
        Arrays.sort(arr);
        int unique = 0;
        for (int value : arr) {
            if (unique == 0 || arr[unique - 1] != value) {
                arr[unique++] = value;
            }
        }
        return Arrays.copyOf(arr, unique);
    }

    private int upperBound(int[] arr, int target) {
        int lo = 0;
        int hi = arr.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (arr[mid] <= target) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }
}
// @lc code=end
