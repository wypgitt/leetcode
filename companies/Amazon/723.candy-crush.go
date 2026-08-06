package leetcode

// CandyCrush723 repeatedly marks all horizontal and vertical runs of at least
// three, crushes them simultaneously, then applies gravity column by column.
// Simultaneous marking is required because one candy can belong to two runs.
//
// Time: O(p*m*n), where p is the number of stabilization passes. Space: O(m*n).
func CandyCrush723(board [][]int) [][]int {
	m, n := len(board), len(board[0])
	for {
		changed := false
		crush := make([][]bool, m)
		for i := range crush {
			crush[i] = make([]bool, n)
		}
		for r := 0; r < m; r++ {
			for c := 0; c < n; {
				c2 := c + 1
				for c2 < n && absInt(board[r][c2]) == absInt(board[r][c]) {
					c2++
				}
				if board[r][c] != 0 && c2-c >= 3 {
					changed = true
					for x := c; x < c2; x++ {
						crush[r][x] = true
					}
				}
				c = c2
			}
		}
		for c := 0; c < n; c++ {
			for r := 0; r < m; {
				r2 := r + 1
				for r2 < m && absInt(board[r2][c]) == absInt(board[r][c]) {
					r2++
				}
				if board[r][c] != 0 && r2-r >= 3 {
					changed = true
					for x := r; x < r2; x++ {
						crush[x][c] = true
					}
				}
				r = r2
			}
		}
		if !changed {
			break
		}
		for c := 0; c < n; c++ {
			write := m - 1
			for r := m - 1; r >= 0; r-- {
				if !crush[r][c] {
					board[write][c] = board[r][c]
					write--
				}
			}
			for r := write; r >= 0; r-- {
				board[r][c] = 0
			}
		}
	}
	return board
}
