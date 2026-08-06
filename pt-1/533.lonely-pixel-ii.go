package leetcode

//
// @lc app=leetcode id=533 lang=golang
//
// [533] Lonely Pixel II
//
// Notes
// Count black pixels in every column and count identical row patterns. A row
// pattern contributes only when it appears exactly target times and contains
// exactly target black pixels; for each black column whose total count is also
// target, all target identical rows contribute. Time: O(RC). Space: O(RC) for
// row-pattern strings.
//
// @lc code=start

func FindBlackPixel533(picture [][]byte, target int) int {
	rows, cols := len(picture), len(picture[0])
	columnBlackCount := make([]int, cols)
	rowCount := map[string]int{}

	for _, row := range picture {
		rowPattern := string(row)
		rowCount[rowPattern]++
		for col, value := range row {
			if value == 'B' {
				columnBlackCount[col]++
			}
		}
	}

	answer := 0
	for rowPattern, occurrences := range rowCount {
		if occurrences != target {
			continue
		}
		if countByte533(rowPattern, 'B') != target {
			continue
		}
		for col := 0; col < cols; col++ {
			if rowPattern[col] == 'B' && columnBlackCount[col] == target {
				answer += target
			}
		}
	}
	_ = rows
	return answer
}

func countByte533(s string, target byte) int {
	count := 0
	for i := range s {
		if s[i] == target {
			count++
		}
	}
	return count
}

// @lc code=end
