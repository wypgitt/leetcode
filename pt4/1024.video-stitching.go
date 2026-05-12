package main

import "sort"

/*
1024. Video Stitching
*/
func videoStitching(clips [][]int, time int) int {
	sort.Slice(clips, func(i, j int) bool {
		if clips[i][0] == clips[j][0] {
			return clips[i][1] < clips[j][1]
		}
		return clips[i][0] < clips[j][0]
	})

	index := 0
	used := 0
	coveredUntil := 0

	for coveredUntil < time {
		farthest := coveredUntil

		for index < len(clips) && clips[index][0] <= coveredUntil {
			if clips[index][1] > farthest {
				farthest = clips[index][1]
			}
			index++
		}

		if farthest == coveredUntil {
			return -1
		}

		used++
		coveredUntil = farthest
	}

	return used
}

/*
Interview Explanation

Core idea:
This is minimum interval coverage. If the current covered prefix is
[0, coveredUntil], the next clip must start at or before coveredUntil. Among
all such clips, choose the one that extends farthest.

Go data structures:
- sort.Slice orders clips by start time.
- Scalar variables track the scan position, clip count, and current coverage.

Algorithm:
1. Sort clips by start.
2. While coverage is short of time, scan every clip that starts within the
   current covered prefix.
3. Record the farthest end reachable by adding one clip.
4. If coverage cannot advance, return -1.
5. Otherwise, use one clip and advance coverage.

Correctness:
Every feasible solution must choose a next clip whose start is at most the
current boundary. Choosing the one with the farthest end covers at least as
much as any other feasible choice, so it cannot make the future worse. Repeating
this greedy choice gives the minimum number of clips. If no clip extends the
boundary, there is a gap and coverage is impossible.

Complexity:
Sorting costs O(n log n), and the scan is O(n). Extra space is O(1) aside from
sorting internals.

Edge cases:
- No clip starts at 0: impossible.
- One clip covers the full event: answer 1.
- Overlapping clips are scanned once.
- Clips may extend past time; the loop stops when coverage reaches time.
*/
