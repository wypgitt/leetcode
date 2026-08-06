package leetcode

// Rotate48 performs a 90-degree clockwise rotation by transposing the square
// matrix in place and then reversing every row. This avoids allocating a second
// matrix.
//
// Time: O(n^2). Space: O(1).
func Rotate48(matrix [][]int) {
	n := len(matrix)
	for r := 0; r < n; r++ {
		for c := r + 1; c < n; c++ {
			matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
		}
	}
	for _, row := range matrix {
		for l, r := 0, len(row)-1; l < r; l, r = l+1, r-1 {
			row[l], row[r] = row[r], row[l]
		}
	}
}
