package leetcode

// Solve130 marks all border-connected 'O' cells as safe with BFS, flips the
// remaining enclosed 'O' cells to 'X', then restores safe cells. Border-connected
// regions cannot be surrounded.
//
// Time: O(m*n). Space: O(m*n) worst-case queue.
func Solve130(board [][]byte) {
	if len(board) == 0 || len(board[0]) == 0 {
		return
	}
	rows, cols := len(board), len(board[0])
	type cell struct{ r, c int }
	q := []cell{}
	mark := func(r, c int) {
		if board[r][c] == 'O' {
			board[r][c] = 'S'
			q = append(q, cell{r, c})
		}
	}
	for r := 0; r < rows; r++ {
		mark(r, 0)
		mark(r, cols-1)
	}
	for c := 0; c < cols; c++ {
		mark(0, c)
		mark(rows-1, c)
	}
	dirs := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}
	for head := 0; head < len(q); head++ {
		cur := q[head]
		for _, d := range dirs {
			nr, nc := cur.r+d[0], cur.c+d[1]
			if nr >= 0 && nr < rows && nc >= 0 && nc < cols && board[nr][nc] == 'O' {
				board[nr][nc] = 'S'
				q = append(q, cell{nr, nc})
			}
		}
	}
	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			if board[r][c] == 'O' {
				board[r][c] = 'X'
			} else if board[r][c] == 'S' {
				board[r][c] = 'O'
			}
		}
	}
}
