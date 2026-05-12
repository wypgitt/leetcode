import java.util.Arrays;

/*
 * 1024. Video Stitching
 */
class Solution {
    public int videoStitching(int[][] clips, int time) {
        Arrays.sort(clips, (a, b) -> a[0] == b[0] ? Integer.compare(a[1], b[1]) : Integer.compare(a[0], b[0]));

        int index = 0;
        int used = 0;
        int coveredUntil = 0;

        while (coveredUntil < time) {
            int farthest = coveredUntil;

            while (index < clips.length && clips[index][0] <= coveredUntil) {
                farthest = Math.max(farthest, clips[index][1]);
                index++;
            }

            if (farthest == coveredUntil) {
                return -1;
            }

            used++;
            coveredUntil = farthest;
        }

        return used;
    }
}

/*
Interview Explanation

Core idea:
This is minimum interval coverage. If the covered prefix is [0, coveredUntil],
the next clip must start at or before coveredUntil. Among all currently usable
clips, choosing the clip that extends farthest is optimal.

Java data structures:
- Arrays.sort orders clips by start time.
- Scalar variables are enough after sorting: index scans clips once, and
  farthest records the best extension.

Algorithm:
1. Sort clips by start time.
2. While the target interval is not fully covered, scan every clip that starts
   before or at the current coverage boundary.
3. Keep the farthest end among those clips.
4. If coverage cannot advance, return -1.
5. Otherwise, commit one clip and move the boundary to farthest.

Correctness:
Every valid solution must choose a next clip starting no later than
coveredUntil. Choosing the one with the farthest end covers at least as much as
any other feasible choice, so it cannot make future coverage harder. Repeating
this greedy choice gives the minimum number of clips. If no clip advances the
boundary, a gap exists and coverage is impossible.

Complexity:
Sorting is O(n log n). The scan is O(n), so total time is O(n log n). Extra
space is O(1) beyond the sorting implementation.

Edge cases:
- No clip starts at 0: impossible.
- One clip covers [0, time]: answer is 1.
- Clips may overlap heavily; each is still scanned once.
- Clips ending beyond time are acceptable.
*/
