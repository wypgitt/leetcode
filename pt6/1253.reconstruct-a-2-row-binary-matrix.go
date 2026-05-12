package main

func reconstructMatrix(upper int, lower int, colsum []int) [][]int {
	top := make([]int, len(colsum))
	bottom := make([]int, len(colsum))

	for i, sum := range colsum {
		if sum == 2 {
			top[i], bottom[i] = 1, 1
			upper--
			lower--
		}
	}
	if upper < 0 || lower < 0 {
		return [][]int{}
	}

	for i, sum := range colsum {
		if sum == 1 {
			if upper > 0 {
				top[i] = 1
				upper--
			} else if lower > 0 {
				bottom[i] = 1
				lower--
			} else {
				return [][]int{}
			}
		}
	}

	if upper != 0 || lower != 0 {
		return [][]int{}
	}
	return [][]int{top, bottom}
}

/*
Explanation

Columns with colsum 2 are forced to be [1,1], so assign those first and reduce
both row budgets. Columns with colsum 1 are interchangeable; greedily place
ones in the upper row until it reaches its budget, then use the lower row.

The greedy step is safe because the remaining single-one columns have no other
constraints besides the row sums.

Edge cases: too many forced 2-columns; not enough colsum 1 columns; leftover
upper or lower budget after assignment.

Time complexity: O(n).
Space complexity: O(n) for the two output rows.
*/
