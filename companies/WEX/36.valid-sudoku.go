package leetcode

// IsValidSudoku36 tracks seen digits for each row, column, and 3x3 box. In Go,
// fixed [9][9]bool arrays are more direct than hash sets because the board and
// digit domain are constant size.
//
// Time/space: O(1) for the fixed 9x9 board.
func IsValidSudoku36(board [][]byte) bool {
	var rows, cols, boxes [9][9]bool
	for r := 0; r < 9; r++ {
		for c := 0; c < 9; c++ {
			val := board[r][c]
			if val == '.' {
				continue
			}
			d := val - '1'
			b := (r/3)*3 + c/3
			if rows[r][d] || cols[c][d] || boxes[b][d] {
				return false
			}
			rows[r][d], cols[c][d], boxes[b][d] = true, true, true
		}
	}
	return true
}
