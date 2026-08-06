package leetcode

// GenerateMatrix59 fills an n by n matrix in spiral order using the same
// shrinking-boundary idea as spiral traversal. Boundaries prevent revisits, so
// no visited set is needed.
//
// Time: O(n^2). Space: O(1) excluding output.
func GenerateMatrix59(n int) [][]int {
	matrix := make([][]int, n)
	for i := range matrix {
		matrix[i] = make([]int, n)
	}
	top, bottom, left, right, val := 0, n-1, 0, n-1, 1
	for top <= bottom && left <= right {
		for c := left; c <= right; c++ {
			matrix[top][c] = val
			val++
		}
		top++
		for r := top; r <= bottom; r++ {
			matrix[r][right] = val
			val++
		}
		right--
		for c := right; c >= left; c-- {
			matrix[bottom][c] = val
			val++
		}
		bottom--
		for r := bottom; r >= top; r-- {
			matrix[r][left] = val
			val++
		}
		left++
	}
	return matrix
}
