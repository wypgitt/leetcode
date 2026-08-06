/*
 * @lc app=leetcode id=3885 lang=java
 *
 * [3885] Design Event Manager
 *
 * Keep active priorities in a HashMap and push every priority update into a
 * heap ordered by highest priority, then smallest eventId. pollHighest lazily
 * discards stale heap entries whose priority no longer matches the active map.
 *
 * Java note: PriorityQueue is a binary heap. Lazy deletion avoids O(log n)
 * arbitrary removal when priorities are updated.
 *
 * Each operation: O(log n) amortized. Space: O(n + updates).
 */

import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;

// @lc code=start
class EventManager {
    private final Map<Integer, Integer> activePriority = new HashMap<>();
    private final PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> {
        if (a[0] != b[0]) {
            return Integer.compare(b[0], a[0]);
        }
        return Integer.compare(a[1], b[1]);
    });

    public EventManager(int[][] events) {
        for (int[] event : events) {
            int eventId = event[0];
            int priority = event[1];
            activePriority.put(eventId, priority);
            heap.offer(new int[] {priority, eventId});
        }
    }

    public void updatePriority(int eventId, int newPriority) {
        activePriority.put(eventId, newPriority);
        heap.offer(new int[] {newPriority, eventId});
    }

    public int pollHighest() {
        while (!heap.isEmpty()) {
            int[] top = heap.poll();
            int priority = top[0];
            int eventId = top[1];
            Integer active = activePriority.get(eventId);
            if (active != null && active == priority) {
                activePriority.remove(eventId);
                return eventId;
            }
        }
        return -1;
    }
}
// @lc code=end
