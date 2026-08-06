package leetcode

// Partition131 precomputes pal[i][j], then backtracks over palindromic cuts.
// The DP table makes each palindrome check O(1), and each valid partition path
// is copied at the end.
//
// Time: O(n^2 + output*n). Space: O(n^2).
func Partition131(s string) [][]string {
	n := len(s)
	pal := make([][]bool, n)
	for i := range pal {
		pal[i] = make([]bool, n)
	}
	for i := n - 1; i >= 0; i-- {
		for j := i; j < n; j++ {
			pal[i][j] = s[i] == s[j] && (j-i < 2 || pal[i+1][j-1])
		}
	}
	ans := [][]string{}
	path := []string{}
	var dfs func(int)
	dfs = func(start int) {
		if start == n {
			ans = append(ans, append([]string(nil), path...))
			return
		}
		for end := start; end < n; end++ {
			if pal[start][end] {
				path = append(path, s[start:end+1])
				dfs(end + 1)
				path = path[:len(path)-1]
			}
		}
	}
	dfs(0)
	return ans
}
