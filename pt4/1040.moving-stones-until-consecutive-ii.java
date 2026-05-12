import java.util.Arrays;

/*
 * 1040. Moving Stones Until Consecutive II
 */
class Solution {
    public int[] numMovesStonesII(int[] stones) {
        Arrays.sort(stones);
        int n = stones.length;

        int maxMoves = Math.max(
            stones[n - 1] - stones[1] + 1 - (n - 1),
            stones[n - 2] - stones[0] + 1 - (n - 1)
        );

        int minMoves = n;
        int left = 0;
        for (int right = 0; right < n; right++) {
            while (stones[right] - stones[left] + 1 > n) {
                left++;
            }

            int stonesInWindow = right - left + 1;
            int windowSize = stones[right] - stones[left] + 1;

            if (stonesInWindow == n - 1 && windowSize == n - 1) {
                minMoves = Math.min(minMoves, 2);
            } else {
                minMoves = Math.min(minMoves, n - stonesInWindow);
            }
        }

        return new int[] {minMoves, maxMoves};
    }
}

/*
Interview Explanation

Core idea:
The final positions must be n consecutive integers. For minimum moves, find a
length-n coordinate window that already contains as many stones as possible.
For maximum moves, leave one endpoint fixed and count how many interior empty
positions can be filled slowly.

Java data structures:
- Arrays.sort gives stone order on the number line.
- Two pointers maintain a sliding window where coordinate width is at most n.

Algorithm:
Minimum:
1. Slide a window while stones[right] - stones[left] + 1 <= n.
2. If k stones are already in that final block, normally n - k stones must move.
3. Special case: n - 1 stones packed into n - 1 positions require 2 moves,
   because the lone endpoint cannot move directly into the only missing slot
   and still stop being an endpoint.

Maximum:
Exclude either the leftmost or rightmost endpoint and count empty positions in
the range occupied by the remaining n - 1 stones. Take the larger count.

Correctness:
Any final configuration is a block of n positions, so stones already inside
the chosen block can stay and all outside stones must move. The sliding window
finds the block with maximum stones, minimizing moves, with the endpoint
legality exception handled explicitly. The maximum formulas count the longest
legal sequence of endpoint moves before the stones become consecutive.

Complexity:
Sorting is O(n log n), and the sliding window is O(n). Extra space is O(1)
apart from sorting.

Edge cases:
- Already consecutive returns [0, 0].
- Almost consecutive such as [1,2,3,4,10] has minimum 2.
- Large coordinates are safe because only differences are used.
*/
