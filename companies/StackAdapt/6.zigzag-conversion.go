package leetcode

import "strings"

// Convert6 keeps one builder per row and simulates the zigzag row movement.
// Builders avoid quadratic string concatenation; direction flips at top/bottom.
//
// Time: O(n). Space: O(n).
func Convert6(s string, numRows int) string {
	if numRows == 1 || numRows >= len(s) {
		return s
	}
	rows := make([]strings.Builder, numRows)
	row, step := 0, 1
	for i := 0; i < len(s); i++ {
		rows[row].WriteByte(s[i])
		if row == 0 {
			step = 1
		} else if row == numRows-1 {
			step = -1
		}
		row += step
	}
	var ans strings.Builder
	for i := range rows {
		ans.WriteString(rows[i].String())
	}
	return ans.String()
}
