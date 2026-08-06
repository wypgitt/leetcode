package leetcode

// SearchMatrix240 starts at the top-right corner. Values left are smaller and
// values below are larger, so each comparison discards one row or one column.
//
// Time: O(m+n). Space: O(1).
func SearchMatrix240(matrix [][]int, target int) bool {
	if len(matrix) == 0 || len(matrix[0]) == 0 {
		return false
	}
	r, c := 0, len(matrix[0])-1
	for r < len(matrix) && c >= 0 {
		v := matrix[r][c]
		if v == target {
			return true
		}
		if v > target {
			c--
		} else {
			r++
		}
	}
	return false
}
