package main

import "sort"

/*
1033. Moving Stones Until Consecutive
*/
func numMovesStones(a int, b int, c int) []int {
	stones := []int{a, b, c}
	sort.Ints(stones)
	x, y, z := stones[0], stones[1], stones[2]

	maxMoves := z - x - 2
	minMoves := 2
	if y == x+1 && z == y+1 {
		minMoves = 0
	} else if y-x <= 2 || z-y <= 2 {
		minMoves = 1
	}

	return []int{minMoves, maxMoves}
}

/*
Interview Explanation

Core idea:
With exactly three stones, sorting exposes both gaps. The final state requires
both gaps to be 1.

Go data structures:
- []int of length three is sorted with sort.Ints.
- No search or graph is needed; the sorted gaps contain all information.

Algorithm:
1. Sort positions x < y < z.
2. Maximum moves are z - x - 2, the number of empty interior positions.
3. Minimum moves:
   - 0 if already consecutive.
   - 1 if either gap is at most 2.
   - 2 otherwise.

Correctness:
If stones are consecutive, no move is needed. If a close pair has gap 1 or 2,
one endpoint can be moved to complete three consecutive positions. If both
gaps are larger, no single endpoint move can fix both gaps, but two moves can.
The maximum counts how many interior empty slots can be consumed before the
game ends.

Complexity:
O(1) time and O(1) space.

Edge cases:
- Unsorted input is handled by sorting.
- Already consecutive returns [0, 0].
- A gap of exactly 2 finishes in one move.
*/
