package main

func equalSubstring(s string, t string, maxCost int) int {
	left, cost, best := 0, 0, 0

	for right := 0; right < len(s); right++ {
		cost += absInt(int(s[right]) - int(t[right]))

		for cost > maxCost {
			cost -= absInt(int(s[left]) - int(t[left]))
			left++
		}

		if length := right - left + 1; length > best {
			best = length
		}
	}

	return best
}

func absInt(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

/*
Explanation

Build the implicit cost array where cost[i] is abs(s[i] - t[i]). The task is
then the longest contiguous subarray whose sum is at most maxCost.

Because every cost is nonnegative, a sliding window is the right data structure:
expanding the right side can only increase the total, and moving the left side
can only decrease it. The invariant after the inner loop is that the current
window is affordable, so right-left+1 is a candidate answer.

In Go, bytes are enough because the input is lowercase English letters. absInt
keeps the ASCII distance calculation explicit.

Edge cases: maxCost == 0 keeps only zero-cost runs; a single character works
naturally; if every character is too expensive, the window shrinks to length 0
and best stays 0.

Time complexity: O(n), since each pointer moves at most n times.
Space complexity: O(1).
*/
