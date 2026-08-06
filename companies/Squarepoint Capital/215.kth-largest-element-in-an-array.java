import java.util.*;

/**
 * Algorithm:
 * Maintain a min-heap of the k largest values seen so far. When heap size
 * exceeds k, remove the smallest. The heap root is then the kth largest.
 *
 * Java data structures:
 * PriorityQueue<Integer> is Java's binary min-heap.
 *
 * Complexity:
 * Time O(n log k), space O(k).
 */
class Solution {
    public int findKthLargest(int[] nums, int k) {
        PriorityQueue<Integer> heap = new PriorityQueue<>();
        for (int num : nums) {
            heap.offer(num);
            if (heap.size() > k) {
                heap.poll();
            }
        }
        return heap.peek();
    }
}

