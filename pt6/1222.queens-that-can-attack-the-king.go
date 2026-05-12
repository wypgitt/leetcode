package main

func queensAttacktheKing(queens [][]int, king []int) [][]int {
	occupied := map[[2]int]bool{}
	for _, q := range queens {
		occupied[[2]int{q[0], q[1]}] = true
	}

	ans := [][]int{}
	dirs := [][2]int{
		{1, 0}, {-1, 0}, {0, 1}, {0, -1},
		{1, 1}, {1, -1}, {-1, 1}, {-1, -1},
	}

	for _, d := range dirs {
		r, c := king[0]+d[0], king[1]+d[1]
		for r >= 0 && r < 8 && c >= 0 && c < 8 {
			if occupied[[2]int{r, c}] {
				ans = append(ans, []int{r, c})
				break
			}
			r += d[0]
			c += d[1]
		}
	}

	return ans
}

/*
Explanation

A queen can attack the king only if it is the first queen seen in one of the
eight row, column, or diagonal directions from the king. Put queen positions in
a set, then scan outward from the king in those eight directions.

Go data structure: map[[2]int]bool is a convenient coordinate set because
fixed-size arrays are comparable map keys.

Edge cases: multiple queens in one direction only the closest one counts; no
queen in a direction contributes nothing; the board is fixed at 8 by 8.

Time complexity: O(1), at most 8 directions times 7 squares.
Space complexity: O(q) for the queen set.
*/
