package leetcode

// SpiralOrder54 consumes a matrix layer by layer using shrinking top, bottom,
// left, and right boundaries. Checks before bottom/left passes avoid rereading a
// final single row or column.
//
// Time: O(m*n). Space: O(1) excluding output.
func SpiralOrder54(matrix [][]int) []int {
	ans := []int{}
	top, bottom := 0, len(matrix)-1
	left, right := 0, len(matrix[0])-1
	for top <= bottom && left <= right {
		for c := left; c <= right; c++ {
			ans = append(ans, matrix[top][c])
		}
		top++
		for r := top; r <= bottom; r++ {
			ans = append(ans, matrix[r][right])
		}
		right--
		if top <= bottom {
			for c := right; c >= left; c-- {
				ans = append(ans, matrix[bottom][c])
			}
			bottom--
		}
		if left <= right {
			for r := bottom; r >= top; r-- {
				ans = append(ans, matrix[r][left])
			}
			left++
		}
	}
	return ans
}
