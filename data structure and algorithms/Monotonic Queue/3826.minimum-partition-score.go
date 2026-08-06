package leetcode

//
// @lc app=leetcode id=3826 lang=golang
//
// [3826] Minimum Partition Score
//
// Notes
// The partition DP can be written with prefix sums as a minimum over lines:
// dp[p][i] = prefix[i]^2 + min_j(-2*prefix[j]*prefix[i] + prev[j]+prefix[j]^2).
// Because lines are added and queried in monotone order, a convex hull stored in
// a slice with a moving head gives amortized O(1) queries per state. int64 is
// used for squared prefix sums. Time: O(kn). Space: O(n).
//
// @lc code=start

type line3826 struct {
	slope     int64
	intercept int64
}

func MinPartitionScore3826(nums []int, k int) int {
	n := len(nums)
	prefix := make([]int64, n+1)
	for i, value := range nums {
		prefix[i+1] = prefix[i] + int64(value)
	}

	const inf int64 = 1 << 62
	prev := make([]int64, n+1)
	for i := range prev {
		prev[i] = inf
	}
	prev[0] = 0

	for parts := 1; parts <= k; parts++ {
		cur := make([]int64, n+1)
		for i := range cur {
			cur[i] = inf
		}
		hull := []line3826{}
		head := 0

		for i := parts; i <= n; i++ {
			cut := i - 1
			addLine3826(&hull, line3826{
				slope:     -2 * prefix[cut],
				intercept: prev[cut] + prefix[cut]*prefix[cut],
			})
			if head >= len(hull) {
				head = len(hull) - 1
			}

			x := prefix[i]
			for head+1 < len(hull) && value3826(hull[head+1], x) <= value3826(hull[head], x) {
				head++
			}
			cur[i] = x*x + value3826(hull[head], x)
		}
		prev = cur
	}

	return int((prev[n] + prefix[n]) / 2)
}

func addLine3826(hull *[]line3826, line line3826) {
	for len(*hull) >= 2 && isBad3826((*hull)[len(*hull)-2], (*hull)[len(*hull)-1], line) {
		*hull = (*hull)[:len(*hull)-1]
	}
	*hull = append(*hull, line)
}

func isBad3826(first, second, third line3826) bool {
	return (second.intercept-first.intercept)*(second.slope-third.slope) >=
		(third.intercept-second.intercept)*(first.slope-second.slope)
}

func value3826(line line3826, x int64) int64 {
	return line.slope*x + line.intercept
}

// @lc code=end
