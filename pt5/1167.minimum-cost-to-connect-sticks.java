import java.util.*;

class Solution {
    public int connectSticks(int[] sticks) {
        PriorityQueue<Integer> heap = new PriorityQueue<>();
        for (int stick : sticks) {
            heap.offer(stick);
        }

        int total = 0;
        while (heap.size() > 1) {
            int first = heap.poll();
            int second = heap.poll();
            int merged = first + second;
            total += merged;
            heap.offer(merged);
        }

        return total;
    }
}

