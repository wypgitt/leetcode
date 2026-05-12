package main

func numOfBurgers(tomatoSlices int, cheeseSlices int) []int {
	extraTomatoes := tomatoSlices - 2*cheeseSlices
	if extraTomatoes < 0 || extraTomatoes%2 != 0 {
		return []int{}
	}

	jumbo := extraTomatoes / 2
	small := cheeseSlices - jumbo
	if small < 0 {
		return []int{}
	}

	return []int{jumbo, small}
}

/*
Explanation

Let jumbo=x and small=y. Then x+y=cheeseSlices and 4x+2y=tomatoSlices.
Subtract 2*(x+y) from the tomato equation and get 2x = tomatoSlices -
2*cheeseSlices. That gives jumbo directly; small is the remaining cheese
count.

Both counts must be nonnegative integers.

Edge cases: too few tomatoes, odd extraTomatoes, or jumbo greater than total
cheese all mean impossible.

Time complexity: O(1).
Space complexity: O(1).
*/
