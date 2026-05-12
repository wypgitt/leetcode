import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/*
 * LeetCode 1338 - Reduce Array Size to The Half
 */
class Solution {
    public int minSetSize(int[] arr) {
        Map<Integer, Integer> frequency = new HashMap<>();
        for (int value : arr) {
            frequency.put(value, frequency.getOrDefault(value, 0) + 1);
        }

        List<Integer> counts = new ArrayList<>(frequency.values());
        counts.sort(Collections.reverseOrder());

        int removed = 0;
        int target = arr.length / 2;
        for (int i = 0; i < counts.size(); i++) {
            removed += counts.get(i);
            if (removed >= target) {
                return i + 1;
            }
        }

        return 0;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Removing one chosen value removes all of its occurrences. To minimize the
 * number of chosen values, greedily remove the most frequent values first.
 *
 * Java data structures:
 * `HashMap<Integer, Integer>` counts frequencies. `ArrayList<Integer>` stores
 * frequencies so we can sort them descending.
 *
 * Why greedy works:
 * Every chosen value costs one slot in the set, so the best immediate benefit
 * is the largest frequency. Taking larger benefits first reaches half the array
 * with the fewest choices.
 *
 * Complexity:
 * Time O(n + u log u), where u is the number of distinct values.
 * Space O(u).
 */
