import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public List<List<Integer>> removeInterval(int[][] intervals, int[] toBeRemoved) {
        int removeStart = toBeRemoved[0];
        int removeEnd = toBeRemoved[1];
        List<List<Integer>> ans = new ArrayList<>();

        for (int[] interval : intervals) {
            int start = interval[0];
            int end = interval[1];

            if (end <= removeStart || start >= removeEnd) {
                ans.add(Arrays.asList(start, end));
                continue;
            }
            if (start < removeStart) {
                ans.add(Arrays.asList(start, removeStart));
            }
            if (removeEnd < end) {
                ans.add(Arrays.asList(removeEnd, end));
            }
        }

        return ans;
    }
}

/*
Explanation

For each interval, compare it with the interval to remove. If there is no
overlap, keep it unchanged. If there is overlap, at most two pieces survive:
the portion before removeStart and the portion after removeEnd.

No interval tree or heap is needed because the input intervals are already
sorted and disjoint.

Edge cases: removal covers an entire interval; removal cuts the middle; removal
touches an endpoint, where zero-length pieces must not be emitted.

Time complexity: O(n).
Space complexity: O(n) for the returned list.
*/
