import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;

/*
 * 1054. Distant Barcodes
 */
class Solution {
    public int[] rearrangeBarcodes(int[] barcodes) {
        Map<Integer, Integer> frequency = new HashMap<>();
        for (int barcode : barcodes) {
            frequency.put(barcode, frequency.getOrDefault(barcode, 0) + 1);
        }

        PriorityQueue<int[]> heap = new PriorityQueue<>(
            (a, b) -> a[0] == b[0] ? Integer.compare(a[1], b[1]) : Integer.compare(b[0], a[0])
        );
        for (Map.Entry<Integer, Integer> entry : frequency.entrySet()) {
            heap.offer(new int[] {entry.getValue(), entry.getKey()});
        }

        int[] result = new int[barcodes.length];
        int index = 0;
        int[] previous = null;

        while (!heap.isEmpty()) {
            int[] current = heap.poll();
            result[index++] = current[1];
            current[0]--;

            if (previous != null && previous[0] > 0) {
                heap.offer(previous);
            }
            previous = current;
        }

        return result;
    }
}

/*
Interview Explanation

Core idea:
Always place the most frequent barcode that is not equal to the previously
placed barcode. Hold the previous barcode out of the heap for one turn so it
cannot be selected immediately again.

Java data structures:
- HashMap<Integer, Integer> counts frequencies.
- PriorityQueue<int[]> acts as a max heap by count.
- previous temporarily stores the last used barcode and its remaining count.

Algorithm:
1. Count every barcode.
2. Push (count, barcode) pairs into a max heap.
3. Poll the most frequent available barcode and append it.
4. Decrement its count.
5. Reinsert the previous barcode after a different barcode has been placed.

Correctness:
The last placed barcode is not in the heap during the next poll, so the
algorithm never places equal adjacent barcodes. Since the problem guarantees a
valid arrangement, repeatedly choosing the highest remaining available count
keeps the most constrained values spread out and completes a valid sequence.

Complexity:
Let n be the number of barcodes and k be the number of distinct values. Time is
O(n log k), and space is O(k) besides the returned array.

Edge cases:
- Length one returns the same value.
- Equal frequencies alternate naturally.
- A dominant value is spread across the result as early as possible.
*/
