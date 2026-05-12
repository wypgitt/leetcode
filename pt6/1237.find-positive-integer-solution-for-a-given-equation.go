package main

type CustomFunction interface {
	f(x int, y int) int
}

func findSolution(customfunction CustomFunction, z int) [][]int {
	ans := [][]int{}
	x, y := 1, 1000

	for x <= 1000 && y >= 1 {
		value := customfunction.f(x, y)
		if value == z {
			ans = append(ans, []int{x, y})
			x++
			y--
		} else if value < z {
			x++
		} else {
			y--
		}
	}

	return ans
}

/*
Explanation

The function is strictly increasing in x and in y. View the possible pairs as a
sorted 1000 by 1000 matrix. Start at x=1, y=1000. If f(x,y) is too small,
increase x. If it is too large, decrease y. If it matches, record the pair and
move both pointers because strict monotonicity prevents another solution with
the same x or y.

This is the classic sorted-matrix corner search and avoids testing one million
pairs.

Edge cases: no solution; solutions on boundaries; multiple solutions along the
monotone frontier.

Time complexity: O(1000), generally O(limit).
Space complexity: O(1) besides output.
*/
