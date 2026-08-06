package leetcode

// GetFactors254 backtracks over nondecreasing factors. Whenever factor divides
// target, factor and target/factor form one combination, and recursion continues
// with factor as the minimum to avoid duplicate orderings.
//
// Time: output-dependent. Space: O(log n) recursion in typical factor chains.
func GetFactors254(n int) [][]int {
	ans := [][]int{}
	var dfs func(int, int, []int)
	dfs = func(start, target int, path []int) {
		for f := start; f*f <= target; f++ {
			if target%f == 0 {
				combo := append(append([]int(nil), path...), f, target/f)
				ans = append(ans, combo)
				dfs(f, target/f, append(append([]int(nil), path...), f))
			}
		}
	}
	dfs(2, n, []int{})
	return ans
}
