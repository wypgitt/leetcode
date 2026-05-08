/*
 * @lc app=leetcode id=3893 lang=java
 *
 * [3893] Maximum Team Size With Overlapping Intervals
 *
 * For each original interval [start, end], count intervals that have started by
 * end minus intervals that ended before start. Sorted starts/ends plus binary
 * search give the number of intervals overlapping that interval.
 *
 * Time: O(n log n). Space: O(n).
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    public int maximumTeamSize(int[] startTime, int[] endTime) {
        int[] starts = startTime.clone();
        int[] ends = endTime.clone();
        Arrays.sort(starts);
        Arrays.sort(ends);

        int best = 1;
        for (int i = 0; i < startTime.length; i++) {
            int startedByEnd = upperBound(starts, endTime[i]);
            int endedBeforeStart = lowerBound(ends, startTime[i]);
            best = Math.max(best, startedByEnd - endedBeforeStart);
        }
        return best;
    }

    private int lowerBound(int[] arr, int target) {
        int lo = 0;
        int hi = arr.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (arr[mid] < target) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
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
