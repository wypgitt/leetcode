import java.util.*;

/**
 * Algorithm:
 * Sort meetings by start time. A min-heap stores current meeting end times.
 * Remove all rooms that have ended before the current meeting starts, then add
 * the current end time. The maximum heap size is the required rooms.
 *
 * Java data structures:
 * PriorityQueue<Integer> is the min-heap of end times.
 *
 * Complexity:
 * Time O(n log n), space O(n).
 */
class Solution {
    public int minMeetingRooms(int[][] intervals) {
        if (intervals.length == 0) {
            return 0;
        }
        Arrays.sort(intervals, Comparator.comparingInt(a -> a[0]));
        PriorityQueue<Integer> heap = new PriorityQueue<>();
        int best = 0;
        for (int[] interval : intervals) {
            int start = interval[0];
            int end = interval[1];
            while (!heap.isEmpty() && heap.peek() <= start) {
                heap.poll();
            }
            heap.offer(end);
            best = Math.max(best, heap.size());
        }
        return best;
    }
}

