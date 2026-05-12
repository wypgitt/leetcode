import java.util.Arrays;
import java.util.Collections;
import java.util.List;

class Solution {
    public List<Integer> minAvailableDuration(int[][] slots1, int[][] slots2, int duration) {
        Arrays.sort(slots1, (a, b) -> Integer.compare(a[0], b[0]));
        Arrays.sort(slots2, (a, b) -> Integer.compare(a[0], b[0]));

        int i = 0;
        int j = 0;
        while (i < slots1.length && j < slots2.length) {
            int start = Math.max(slots1[i][0], slots2[j][0]);
            int end = Math.min(slots1[i][1], slots2[j][1]);

            if (end - start >= duration) {
                return Arrays.asList(start, start + duration);
            }

            if (slots1[i][1] < slots2[j][1]) {
                i++;
            } else {
                j++;
            }
        }

        return Collections.emptyList();
    }
}

/*
Explanation

Sort both availability lists and scan them with two pointers. The overlap of
current slots is [max(starts), min(ends)]. If it has enough length, it is the
earliest possible meeting because both lists are processed in time order.

If the overlap is too short, advance the slot that ends earlier; that slot
cannot help with any later slot from the other person.

Java choices: Arrays.sort with a comparator sorts primitive 2D arrays by start
time, and Arrays.asList returns the required two-element List.

Edge cases: exact-duration overlap is valid; no match returns an empty list;
unsorted input is normalized by sorting.

Time complexity: O(n log n + m log m).
Space complexity: O(1) besides sorting stack.
*/
