import java.util.*;

/**
 * Algorithm:
 * Scan in three phases: intervals ending before the new interval, intervals
 * overlapping it, and intervals after it. Only the overlapping phase changes
 * the new interval's boundaries.
 *
 * Complexity:
 * Time O(n), output space O(n).
 */
class Solution {
    public int[][] insert(int[][] intervals, int[] newInterval) {
        List<int[]> ans = new ArrayList<>();
        int i = 0;
        int start = newInterval[0];
        int end = newInterval[1];
        while (i < intervals.length && intervals[i][1] < start) {
            ans.add(intervals[i++]);
        }
        while (i < intervals.length && intervals[i][0] <= end) {
            start = Math.min(start, intervals[i][0]);
            end = Math.max(end, intervals[i][1]);
            i++;
        }
        ans.add(new int[] {start, end});
        while (i < intervals.length) {
            ans.add(intervals[i++]);
        }
        return ans.toArray(new int[ans.size()][]);
    }
}

