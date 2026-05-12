import java.util.Arrays;
import java.util.PriorityQueue;

/*
 * LeetCode 1353 - Maximum Number of Events That Can Be Attended
 */
class Solution {
    public int maxEvents(int[][] events) {
        Arrays.sort(events, (a, b) -> Integer.compare(a[0], b[0]));

        PriorityQueue<Integer> minEndDays = new PriorityQueue<>();
        int day = 0;
        int index = 0;
        int attended = 0;

        while (index < events.length || !minEndDays.isEmpty()) {
            if (minEndDays.isEmpty()) {
                day = Math.max(day, events[index][0]);
            }

            while (index < events.length && events[index][0] <= day) {
                minEndDays.offer(events[index][1]);
                index++;
            }

            while (!minEndDays.isEmpty() && minEndDays.peek() < day) {
                minEndDays.poll();
            }

            if (!minEndDays.isEmpty()) {
                minEndDays.poll();
                attended++;
                day++;
            }
        }

        return attended;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Greedy by earliest ending event. On each day, among all events that have
 * started and not expired, attend the one with the smallest end day. This
 * leaves later-ending events available for future days.
 *
 * Java data structures:
 * Sort the events by start day. A `PriorityQueue<Integer>` stores end days of
 * currently available events, with the earliest end day at the top.
 *
 * Edge cases:
 * - Gaps between event days are handled by jumping `day` to the next event
 *   start when the heap is empty.
 * - Expired events are removed before choosing.
 * - Same-day events are handled by the heap ordering.
 *
 * Complexity:
 * Time O(n log n), from sorting and heap operations.
 * Space O(n), for the heap.
 */
