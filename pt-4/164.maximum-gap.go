package leetcode

// MaximumGap164 uses bucket spacing from the pigeonhole principle. The maximum
// adjacent sorted gap must occur between non-empty buckets, so each bucket only
// stores its min and max.
//
// Time: O(n). Space: O(n).
func MaximumGap164(nums []int) int {
	n := len(nums)
	if n < 2 {
		return 0
	}
	lo, hi := nums[0], nums[0]
	for _, x := range nums {
		lo = minInt(lo, x)
		hi = maxInt(hi, x)
	}
	if lo == hi {
		return 0
	}
	size := maxInt(1, (hi-lo+n-2)/(n-1))
	count := (hi-lo)/size + 1
	bmin := make([]int, count)
	bmax := make([]int, count)
	used := make([]bool, count)
	for _, x := range nums {
		i := (x - lo) / size
		if !used[i] {
			bmin[i], bmax[i], used[i] = x, x, true
		} else {
			bmin[i] = minInt(bmin[i], x)
			bmax[i] = maxInt(bmax[i], x)
		}
	}
	best := 0
	prevSet := false
	prev := 0
	for i := 0; i < count; i++ {
		if !used[i] {
			continue
		}
		if prevSet {
			best = maxInt(best, bmin[i]-prev)
		}
		prev = bmax[i]
		prevSet = true
	}
	return best
}
