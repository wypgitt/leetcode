/*
 * @lc app=leetcode id=3802 lang=java
 *
 * [3802] Number of Ways to Paint Sheets
 *
 * For each split x, count colors whose limits can cover x and n-x; subtract
 * same-color choices that can cover both. The counts change only at limit
 * boundaries, so process compressed intervals of x values.
 *
 * Java note: TreeSet gathers sorted breakpoints, and lowerBound on the sorted
 * limit array gives the number of limits >= need.
 *
 * Time: O(m log m). Space: O(m).
 */

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.TreeSet;

// @lc code=start
class Solution {
    private static final int MOD = 1_000_000_007;

    public int numberOfWays(int n, int[] limit) {
        Arrays.sort(limit);
        int m = limit.length;

        TreeSet<Integer> boundarySet = new TreeSet<>();
        boundarySet.add(1);
        boundarySet.add(n);
        for (int value : limit) {
            int[] candidates = {value, value + 1, n - value, n - value + 1};
            for (int point : candidates) {
                if (1 <= point && point <= n) {
                    boundarySet.add(point);
                }
            }
        }

        List<Integer> points = new ArrayList<>(boundarySet);
        long answer = 0;
        for (int i = 0; i + 1 < points.size(); i++) {
            int left = points.get(i);
            int right = points.get(i + 1);
            if (left > n - 1) {
                break;
            }
            int length = Math.min(right, n) - left;
            if (length <= 0) {
                continue;
            }

            long firstChoices = countAtLeast(limit, left, m);
            long secondChoices = countAtLeast(limit, n - left, m);
            long sameColor = countAtLeast(limit, Math.max(left, n - left), m);
            long perSplit = firstChoices * secondChoices - sameColor;
            answer = (answer + perSplit % MOD * length) % MOD;
        }
        return (int) answer;
    }

    private int countAtLeast(int[] limits, int need, int size) {
        return size - lowerBound(limits, need);
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
}
// @lc code=end
