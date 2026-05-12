package main

import "sort"

/*
1040. Moving Stones Until Consecutive II
*/
func numMovesStonesII(stones []int) []int {
	sort.Ints(stones)
	n := len(stones)

	maxLeftExcluded := stones[n-1] - stones[1] + 1 - (n - 1)
	maxRightExcluded := stones[n-2] - stones[0] + 1 - (n - 1)
	maxMoves := maxLeftExcluded
	if maxRightExcluded > maxMoves {
		maxMoves = maxRightExcluded
	}

	minMoves := n
	left := 0
	for right := 0; right < n; right++ {
		for stones[right]-stones[left]+1 > n {
			left++
		}

		stonesInWindow := right - left + 1
		windowSize := stones[right] - stones[left] + 1
		candidate := n - stonesInWindow
		if stonesInWindow == n-1 && windowSize == n-1 {
			candidate = 2
		}
		if candidate < minMoves {
			minMoves = candidate
		}
	}

	return []int{minMoves, maxMoves}
}

/*
Interview Explanation

Core idea:
The final arrangement is n consecutive positions. For minimum moves, find the
length-n coordinate window containing the most stones already. For maximum
moves, leave one endpoint fixed and count interior empty positions that can be
filled slowly.

Go data structures:
- sort.Ints orders stones on the number line.
- Two pointers maintain a sliding window whose coordinate width is at most n.

Algorithm:
Minimum:
1. Slide a window with stones[right] - stones[left] + 1 <= n.
2. If k stones are in that final block, normally n-k stones must move.
3. Handle the special case where n-1 stones occupy n-1 consecutive positions;
   the lone endpoint needs two moves because it cannot move directly to the
   only missing endpoint slot.

Maximum:
Exclude the leftmost endpoint or the rightmost endpoint, count empty positions
in the remaining range, and take the larger count.

Correctness:
Any final configuration is a block of n consecutive coordinates. Stones
already inside that block can stay; stones outside must move. The sliding
window finds the block with the most stones, minimizing moves, with the
endpoint exception handled explicitly. The maximum formulas count the longest
legal sequence of moves before the stones become consecutive.

Complexity:
Sorting costs O(n log n). The two-pointer scan is O(n). Extra space is O(1)
besides sorting.

Edge cases:
- Already consecutive returns [0, 0].
- Almost consecutive like [1,2,3,4,10] has minimum 2.
- Large coordinates are safe because only differences are used.
*/
