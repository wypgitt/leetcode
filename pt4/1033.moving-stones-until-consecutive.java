import java.util.Arrays;

/*
 * 1033. Moving Stones Until Consecutive
 */
class Solution {
    public int[] numMovesStones(int a, int b, int c) {
        int[] stones = {a, b, c};
        Arrays.sort(stones);
        int x = stones[0];
        int y = stones[1];
        int z = stones[2];

        int maxMoves = z - x - 2;
        int minMoves;

        if (y == x + 1 && z == y + 1) {
            minMoves = 0;
        } else if (y - x <= 2 || z - y <= 2) {
            minMoves = 1;
        } else {
            minMoves = 2;
        }

        return new int[] {minMoves, maxMoves};
    }
}

/*
Interview Explanation

Core idea:
With exactly three stones, sorting exposes the entire problem. The two gaps
determine both the minimum and maximum moves.

Java data structures:
- A length-three int[] is sorted with Arrays.sort.
- No graph or search is needed because the state space collapses to gap math.

Algorithm:
1. Sort positions x < y < z.
2. Maximum moves are z - x - 2, the number of empty positions between the
   endpoints.
3. Minimum moves:
   - 0 if already consecutive.
   - 1 if either gap is 1 or 2.
   - 2 otherwise.

Correctness:
If already consecutive, no move is possible. If a gap is at most 2, one
endpoint can be moved into the missing position beside the close pair. If both
gaps are larger than 2, one move cannot fix both gaps, but two endpoint moves
can. The maximum is achieved by filling interior empty positions as slowly as
possible.

Complexity:
O(1) time and O(1) space.

Edge cases:
- Input can be unsorted.
- Already consecutive returns [0, 0].
- Gaps of exactly 2 allow finishing in one move.
*/
