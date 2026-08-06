package leetcode

// GenerateParenthesis22 backtracks only through valid prefixes: opens cannot
// exceed n and closes cannot exceed opens. This directly generates Catalan-size
// output without testing invalid strings.
//
// Time: O(Cn*n). Space: O(n) recursion excluding output.
func GenerateParenthesis22(n int) []string {
	ans := []string{}
	path := []byte{}
	var dfs func(int, int)
	dfs = func(opened, closed int) {
		if len(path) == 2*n {
			ans = append(ans, string(path))
			return
		}
		if opened < n {
			path = append(path, '(')
			dfs(opened+1, closed)
			path = path[:len(path)-1]
		}
		if closed < opened {
			path = append(path, ')')
			dfs(opened, closed+1)
			path = path[:len(path)-1]
		}
	}
	dfs(0, 0)
	return ans
}
