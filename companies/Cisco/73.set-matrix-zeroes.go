package leetcode

// SetZeroes73 uses the first row and first column as marker arrays. Separate
// booleans remember whether those marker row/column themselves must be zeroed,
// because matrix[0][0] is shared by both marker roles.
//
// Time: O(m*n). Space: O(1).
func SetZeroes73(matrix [][]int) {
	m, n := len(matrix), len(matrix[0])
	firstCol, firstRow := false, false
	for r := 0; r < m; r++ {
		if matrix[r][0] == 0 {
			firstCol = true
		}
	}
	for c := 0; c < n; c++ {
		if matrix[0][c] == 0 {
			firstRow = true
		}
	}
	for r := 1; r < m; r++ {
		for c := 1; c < n; c++ {
			if matrix[r][c] == 0 {
				matrix[r][0] = 0
				matrix[0][c] = 0
			}
		}
	}
	for r := 1; r < m; r++ {
		for c := 1; c < n; c++ {
			if matrix[r][0] == 0 || matrix[0][c] == 0 {
				matrix[r][c] = 0
			}
		}
	}
	if firstRow {
		for c := 0; c < n; c++ {
			matrix[0][c] = 0
		}
	}
	if firstCol {
		for r := 0; r < m; r++ {
			matrix[r][0] = 0
		}
	}
}
