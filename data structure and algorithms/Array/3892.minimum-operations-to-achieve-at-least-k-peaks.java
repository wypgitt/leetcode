/*
 * @lc app=leetcode id=3892 lang=java
 *
 * [3892] Minimum Operations to Achieve At Least K Peaks
 *
 * Circular peaks: greedy min-cost with lazy heap and linked ring merge.
 */

import java.util.PriorityQueue;

// @lc code=start
class Solution {
    public long minOperations(int[] nums, int k) {
        int n = nums.length;
        if (k == 0) {
            return 0;
        }
        if (2 * k > n) {
            return -1;
        }

        boolean[] lookup = new boolean[n];
        int[] left = new int[n];
        int[] right = new int[n];
        long[] cost = new long[n];

        for (int i = 0; i < n; i++) {
            left[i] = (i - 1 + n) % n;
            right[i] = (i + 1) % n;
            int nl = nums[left[i]];
            int nr = nums[right[i]];
            cost[i] = Math.max(0, (long) Math.max(nl, nr) + 1 - nums[i]);
        }

        PriorityQueue<long[]> heap = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        for (int i = 0; i < n; i++) {
            heap.offer(new long[] {cost[i], i});
        }

        long result = 0;
        int remaining = k;

        while (!heap.isEmpty()) {
            long[] top = heap.poll();
            long c = top[0];
            int i = (int) top[1];
            if (lookup[i]) {
                continue;
            }
            result += c;
            remaining--;
            if (remaining == 0) {
                return result;
            }

            cost[i] = cost[left[i]] + cost[right[i]] - cost[i];
            heap.offer(new long[] {cost[i], i});

            lookup[left[i]] = true;
            lookup[right[i]] = true;

            left[i] = left[left[i]];
            right[i] = right[right[i]];
            right[left[i]] = i;
            left[right[i]] = i;
        }

        return -1;
    }
}
// @lc code=end
