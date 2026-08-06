package leetcode

// SoupServings808 scales all amounts by 25 and memoizes the probability state
// (a,b). Base cases return 1 when A empties first, 0 when B empties first, and
// 0.5 when both empty together. For large n, the answer is within 1e-5 of 1.
//
// Time/space: O(u^2) below cutoff, u=ceil(n/25).
func SoupServings808(n int) float64 {
	if n > 4800 {
		return 1.0
	}
	units := (n + 24) / 25
	type state struct{ a, b int }
	memo := map[state]float64{}
	servings := [][2]int{{4, 0}, {3, 1}, {2, 2}, {1, 3}}
	var dp func(int, int) float64
	dp = func(a, b int) float64 {
		if a <= 0 && b <= 0 {
			return 0.5
		}
		if a <= 0 {
			return 1.0
		}
		if b <= 0 {
			return 0.0
		}
		key := state{a, b}
		if v, ok := memo[key]; ok {
			return v
		}
		ans := 0.0
		for _, s := range servings {
			ans += dp(a-s[0], b-s[1])
		}
		ans *= 0.25
		memo[key] = ans
		return ans
	}
	return dp(units, units)
}
