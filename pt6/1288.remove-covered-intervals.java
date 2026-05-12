import java.util.Arrays;

class Solution {
    public int removeCoveredIntervals(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> {
            if (a[0] != b[0]) {
                return Integer.compare(a[0], b[0]);
            }
            return Integer.compare(b[1], a[1]);
        });

        int remaining = 0;
        int farthestEnd = 0;
        for (int[] interval : intervals) {
            if (interval[1] > farthestEnd) {
                remaining++;
                farthestEnd = interval[1];
            }
        }

        return remaining;
    }
}

/*
Explanation

Sort intervals by start ascending and end descending. With that order, if an
interval's end is not greater than the farthest end seen so far, it is covered
by an earlier interval. Otherwise it survives.

Sorting end descending for equal starts is important: [1,4] must come before
[1,3] so the shorter one is detected as covered.

Edge cases: same starting point; disjoint intervals; partial overlap without
full coverage.

Time complexity: O(n log n).
Space complexity: O(1) besides sorting stack.
*/
