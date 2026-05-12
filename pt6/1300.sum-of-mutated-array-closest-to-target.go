package main

func findBestValue(arr []int, target int) int {
	right := 0
	for _, num := range arr {
		if num > right {
			right = num
		}
	}

	left := 0
	for left < right {
		mid := left + (right-left)/2
		if mutatedSum(arr, mid) < target {
			left = mid + 1
		} else {
			right = mid
		}
	}

	upper := left
	lower := upper - 1
	if lower < 0 {
		lower = 0
	}

	if abs(mutatedSum(arr, lower)-target) <= abs(mutatedSum(arr, upper)-target) {
		return lower
	}
	return upper
}

func mutatedSum(arr []int, value int) int {
	total := 0
	for _, num := range arr {
		if num < value {
			total += num
		} else {
			total += value
		}
	}
	return total
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

/*
Explanation

For a chosen value v, the mutated sum is sum(min(num, v)). This sum is
monotonic nondecreasing as v grows, so binary search for the smallest v whose
sum is at least target.

The closest answer must be either that v or v-1. Values farther below cannot
be closer on the low side, and values above v only increase the high-side
distance. Compare both and return the smaller value on ties.

Edge cases: target larger than the original array sum; target very small;
exact matches.

Time complexity: O(n log max(arr)).
Space complexity: O(1).
*/
