package leetcode

// SplitIntoFibonacci842 backtracks over possible next numbers. After two values
// are chosen, the next value is forced to their sum, which prunes branches. Each
// value must fit in signed 32-bit range and leading zeros are only valid for 0.
//
// Time: practically O(n^2) choices for first two splits. Space: O(n) output and
// recursion depth.
func SplitIntoFibonacci842(num string) []int {
	ans := []int{}
	const limit = 1<<31 - 1
	var dfs func(int) bool
	dfs = func(pos int) bool {
		if pos == len(num) {
			return len(ans) >= 3
		}
		value := 0
		for end := pos; end < len(num); end++ {
			if end > pos && num[pos] == '0' {
				break
			}
			value = value*10 + int(num[end]-'0')
			if value > limit {
				break
			}
			if len(ans) >= 2 {
				expected := ans[len(ans)-1] + ans[len(ans)-2]
				if value < expected {
					continue
				}
				if value > expected {
					break
				}
			}
			ans = append(ans, value)
			if dfs(end + 1) {
				return true
			}
			ans = ans[:len(ans)-1]
		}
		return false
	}
	dfs(0)
	return ans
}
