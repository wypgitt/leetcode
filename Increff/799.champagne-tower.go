package leetcode

// ChampagneTower799 simulates flow row by row. A glass keeps one cup and splits
// overflow equally to the two glasses below. Only the previous row is needed.
//
// Time: O(query_row^2). Space: O(query_row).
func ChampagneTower799(poured int, queryRow int, queryGlass int) float64 {
	row := []float64{float64(poured)}
	for r := 0; r < queryRow; r++ {
		next := make([]float64, len(row)+1)
		for i, amount := range row {
			overflow := (amount - 1.0) / 2.0
			if overflow < 0 {
				overflow = 0
			}
			next[i] += overflow
			next[i+1] += overflow
		}
		row = next
	}
	if row[queryGlass] > 1.0 {
		return 1.0
	}
	return row[queryGlass]
}
