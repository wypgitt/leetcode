/*
 * @lc app=leetcode id=3768 lang=java
 *
 * [3768] Minimum Inversion Count in Subarrays of Fixed Length
 *
 * Coordinate-compress values and maintain the current length-k window in a
 * Fenwick tree. When sliding, subtract inversions contributed by the outgoing
 * leftmost value and add inversions created by the incoming rightmost value.
 *
 * Java note: Fenwick tree (Binary Indexed Tree) stores frequencies by rank and
 * answers prefix/range counts in O(log n).
 *
 * Time: O(n log n). Space: O(n).
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    public long minInversionCount(int[] nums, int k) {
        if (k == 1) {
            return 0;
        }

        int[] sorted = nums.clone();
        Arrays.sort(sorted);
        int unique = 0;
        for (int value : sorted) {
            if (unique == 0 || sorted[unique - 1] != value) {
                sorted[unique++] = value;
            }
        }
        int[] values = Arrays.copyOf(sorted, unique);

        int n = nums.length;
        int[] ranks = new int[n];
        for (int i = 0; i < n; i++) {
            ranks[i] = lowerBound(values, nums[i]) + 1;
        }

        Fenwick fenwick = new Fenwick(unique);
        long current = 0;
        for (int i = 0; i < k; i++) {
            int rank = ranks[i];
            long greater = i - fenwick.prefixSum(rank);
            current += greater;
            fenwick.add(rank, 1);
        }

        long answer = current;
        for (int right = k; right < n; right++) {
            int left = right - k;

            int outgoingRank = ranks[left];
            current -= fenwick.prefixSum(outgoingRank - 1);
            fenwick.add(outgoingRank, -1);

            int incomingRank = ranks[right];
            long greater = (k - 1L) - fenwick.prefixSum(incomingRank);
            current += greater;
            fenwick.add(incomingRank, 1);

            answer = Math.min(answer, current);
        }
        return answer;
    }

    private int lowerBound(int[] values, int target) {
        int lo = 0;
        int hi = values.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (values[mid] < target) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }

    private static class Fenwick {
        private final int[] tree;

        Fenwick(int size) {
            tree = new int[size + 1];
        }

        void add(int index, int delta) {
            while (index < tree.length) {
                tree[index] += delta;
                index += index & -index;
            }
        }

        int prefixSum(int index) {
            int total = 0;
            while (index > 0) {
                total += tree[index];
                index -= index & -index;
            }
            return total;
        }
    }
}
// @lc code=end
