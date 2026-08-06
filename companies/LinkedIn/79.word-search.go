package leetcode

// Exist79 uses DFS backtracking from each matching start cell. The board cell is
// temporarily marked as visited and restored after exploring four directions. A
// frequency precheck rejects impossible words early.
//
// Time: O(m*n*4^L) worst case. Space: O(L) recursion.
func Exist79(board [][]byte, word string) bool {
	m, n := len(board), len(board[0])
	var bc, wc [256]int
	for r := 0; r < m; r++ {
		for c := 0; c < n; c++ {
			bc[board[r][c]]++
		}
	}
	for i := 0; i < len(word); i++ {
		wc[word[i]]++
	}
	for i := 0; i < 256; i++ {
		if wc[i] > bc[i] {
			return false
		}
	}
	var dfs func(int, int, int) bool
	dfs = func(r, c, idx int) bool {
		if idx == len(word) {
			return true
		}
		if r < 0 || r == m || c < 0 || c == n || board[r][c] != word[idx] {
			return false
		}
		saved := board[r][c]
		board[r][c] = '#'
		found := dfs(r+1, c, idx+1) || dfs(r-1, c, idx+1) || dfs(r, c+1, idx+1) || dfs(r, c-1, idx+1)
		board[r][c] = saved
		return found
	}
	for r := 0; r < m; r++ {
		for c := 0; c < n; c++ {
			if dfs(r, c, 0) {
				return true
			}
		}
	}
	return false
}
