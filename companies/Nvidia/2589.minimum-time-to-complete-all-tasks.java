/*
 * @lc app=leetcode id=2589 lang=java
 *
 * [2589] Minimum Time to Complete All Tasks
 */

/*
 * Sort tasks by end ascending. Greedy: for each task, reuse already "on" seconds in
 * {@code [start, end]}, then turn on as late as possible from {@code end} downward.
 * Constraints bound time by ~2000.
 *
 * Time: O(n log n + n · U). Space: O(U) for the timeline.
 * =============================================================================
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    private static final int MAX_T = 2000;

    public int findMinimumTime(int[][] tasks) {
        Arrays.sort(tasks, (a, b) -> Integer.compare(a[1], b[1]));
        boolean[] on = new boolean[MAX_T + 1];

        for (int[] task : tasks) {
            int start = task[0];
            int end = task[1];
            int duration = task[2];
            int already = 0;
            for (int i = start; i <= end; i++) {
                if (on[i]) {
                    already++;
                }
            }
            int need = duration - already;
            int t = end;
            while (need > 0) {
                if (!on[t]) {
                    on[t] = true;
                    need--;
                }
                t--;
            }
        }

        int ans = 0;
        for (boolean b : on) {
            if (b) {
                ans++;
            }
        }
        return ans;
    }
}
// @lc code=end
