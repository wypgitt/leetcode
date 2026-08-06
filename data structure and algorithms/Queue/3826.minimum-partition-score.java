/*
 * @lc app=leetcode id=3826 lang=java
 *
 * [3826] Minimum Partition Score
 *
 * DP over partition count can be written with prefix sums as a minimum of
 * lines: dp[j] + prefix[j]^2 - 2 * prefix[j] * prefix[i]. A monotone convex
 * hull optimizes each layer because slopes are added in sorted order and
 * queries also move by increasing prefix.
 *
 * Java note: ArrayDeque stores the lower hull of lines and supports O(1)
 * amortized front pops for monotone queries.
 *
 * Time: O(k n). Space: O(n).
 */

import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;

// @lc code=start
class Solution {
    public long minPartitionScore(int[] nums, int k) {
        int n = nums.length;
        long[] prefix = new long[n + 1];
        for (int i = 0; i < n; i++) {
            prefix[i + 1] = prefix[i] + nums[i];
        }

        long inf = Long.MAX_VALUE / 4;
        long[] prev = new long[n + 1];
        Arrays.fill(prev, inf);
        prev[0] = 0;

        for (int parts = 1; parts <= k; parts++) {
            long[] cur = new long[n + 1];
            Arrays.fill(cur, inf);
            Deque<Line> hull = new ArrayDeque<>();

            for (int i = parts; i <= n; i++) {
                int cut = i - 1;
                addLine(hull, new Line(-2 * prefix[cut], prev[cut] + prefix[cut] * prefix[cut]));

                long x = prefix[i];
                while (hull.size() >= 2) {
                    Line first = hull.removeFirst();
                    Line second = hull.peekFirst();
                    if (second.value(x) <= first.value(x)) {
                        continue;
                    }
                    hull.addFirst(first);
                    break;
                }
                cur[i] = x * x + hull.peekFirst().value(x);
            }
            prev = cur;
        }
        return (prev[n] + prefix[n]) / 2;
    }

    private void addLine(Deque<Line> hull, Line line) {
        while (hull.size() >= 2) {
            Line last = hull.removeLast();
            Line before = hull.peekLast();
            if (isBad(before, last, line)) {
                continue;
            }
            hull.addLast(last);
            break;
        }
        hull.addLast(line);
    }

    private boolean isBad(Line first, Line second, Line third) {
        return (second.b - first.b) * (second.m - third.m) >= (third.b - second.b) * (first.m - second.m);
    }

    private static class Line {
        final long m;
        final long b;

        Line(long m, long b) {
            this.m = m;
            this.b = b;
        }

        long value(long x) {
            return m * x + b;
        }
    }
}
// @lc code=end
