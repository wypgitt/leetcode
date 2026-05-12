/*
 * 1041. Robot Bounded In Circle
 */
class Solution {
    public boolean isRobotBounded(String instructions) {
        int x = 0;
        int y = 0;
        int direction = 0;
        int[][] moves = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};

        for (int i = 0; i < instructions.length(); i++) {
            char instruction = instructions.charAt(i);
            if (instruction == 'G') {
                x += moves[direction][0];
                y += moves[direction][1];
            } else if (instruction == 'L') {
                direction = (direction + 3) % 4;
            } else {
                direction = (direction + 1) % 4;
            }
        }

        return (x == 0 && y == 0) || direction != 0;
    }
}

/*
Interview Explanation

Core idea:
Simulate one instruction cycle. The robot is bounded if it returns to the
origin, or if it ends facing a direction other than north. A changed direction
rotates the displacement on repeated cycles and closes within at most four
cycles.

Java data structures:
- int[][] moves maps direction index to (dx, dy).
- direction is an integer modulo 4: north, east, south, west.

Algorithm:
1. Start at (0, 0), facing north.
2. Simulate each character once.
3. Return true if position is origin or direction changed.

Correctness:
If one cycle returns to the origin, repeated cycles stay bounded. If one cycle
does not return but changes direction, future cycles apply the same movement
rotated, so the net displacement cancels after four cycles. If position is not
origin and direction is still north, each cycle adds the same displacement,
making the path unbounded.

Complexity:
Time is O(n), space is O(1).

Edge cases:
- Only turns are bounded.
- "GG" is unbounded.
- "GL" is bounded even though it is not back at origin after one cycle.
*/
