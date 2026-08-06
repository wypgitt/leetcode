import java.util.*;

/**
 * Algorithm:
 * For each denominator j, fractions arr[i] / arr[j] increase as i increases.
 * Seed a min-heap with arr[0] / arr[j], pop the smallest k - 1 fractions, and
 * push the next numerator for the same denominator when valid.
 *
 * Java data structures:
 * PriorityQueue<int[]> stores numerator and denominator indices. The comparator
 * uses cross multiplication to avoid floating-point precision issues.
 *
 * Complexity:
 * Time O((n + k) log n), space O(n).
 */
class Solution {
    public int[] kthSmallestPrimeFraction(int[] arr, int k) {
        int n = arr.length;
        PriorityQueue<int[]> heap = new PriorityQueue<>(
            (a, b) -> Integer.compare(arr[a[0]] * arr[b[1]], arr[b[0]] * arr[a[1]])
        );
        for (int j = 1; j < n; j++) {
            heap.offer(new int[] {0, j});
        }
        for (int count = 0; count < k - 1; count++) {
            int[] cur = heap.poll();
            int i = cur[0];
            int j = cur[1];
            if (i + 1 < j) {
                heap.offer(new int[] {i + 1, j});
            }
        }
        int[] cur = heap.poll();
        return new int[] {arr[cur[0]], arr[cur[1]]};
    }
}

