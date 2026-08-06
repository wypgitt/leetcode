package leetcode

// Flipgame822 bans values that appear on both sides of the same card, because
// they can never be hidden from all fronts. The answer is the smallest value on
// any side that is not banned.
//
// Time: O(n). Space: O(n).
func Flipgame822(fronts []int, backs []int) int {
	banned := map[int]bool{}
	for i, f := range fronts {
		if f == backs[i] {
			banned[f] = true
		}
	}
	ans := 1<<31 - 1
	for _, x := range fronts {
		if !banned[x] && x < ans {
			ans = x
		}
	}
	for _, x := range backs {
		if !banned[x] && x < ans {
			ans = x
		}
	}
	if ans == 1<<31-1 {
		return 0
	}
	return ans
}
