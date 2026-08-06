package leetcode

// LongestConsecutive128 stores all values in a hash set and only starts counting
// at numbers that have no predecessor. Each consecutive run is then walked once
// from its smallest value.
//
// Go data structure note: map[int]bool is the idiomatic hash set.
// Time: O(n) average. Space: O(n).
func LongestConsecutive128(nums []int) int {
	set := map[int]bool{}
	for _, x := range nums {
		set[x] = true
	}
	best := 0
	for x := range set {
		if set[x-1] {
			continue
		}
		length := 1
		for set[x+length] {
			length++
		}
		best = maxInt(best, length)
	}
	return best
}
