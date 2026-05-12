package main

/*
1041. Robot Bounded In Circle
*/
func isRobotBounded(instructions string) bool {
	x, y := 0, 0
	direction := 0
	moves := [][2]int{{0, 1}, {1, 0}, {0, -1}, {-1, 0}}

	for i := 0; i < len(instructions); i++ {
		switch instructions[i] {
		case 'G':
			x += moves[direction][0]
			y += moves[direction][1]
		case 'L':
			direction = (direction + 3) % 4
		case 'R':
			direction = (direction + 1) % 4
		}
	}

	return (x == 0 && y == 0) || direction != 0
}

/*
Interview Explanation

Core idea:
Simulate one instruction cycle. The robot is bounded if it returns to the
origin, or if it finishes facing a direction other than north. A changed
direction rotates repeated displacements and closes within at most four cycles.

Go data structures:
- [][2]int maps direction index to movement vector.
- direction is an integer modulo 4: north, east, south, west.

Algorithm:
1. Start at (0,0) facing north.
2. Execute the instruction string once.
3. Return true if the robot is back at origin or no longer facing north.

Correctness:
If one cycle returns to origin, repetition stays bounded. If one cycle changes
direction, future cycles apply the same displacement rotated, and the net
displacement cancels after at most four cycles. If the robot is not at origin
and still faces north, each repetition adds the same displacement forever, so
it is unbounded.

Complexity:
Time is O(n), and space is O(1).

Edge cases:
- Only turns are bounded.
- "GG" is unbounded.
- "GL" is bounded despite not returning after one cycle.
*/
