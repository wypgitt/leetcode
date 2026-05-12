package main

import "math"

func maxSumDivThree(nums []int) int {
	dp := [3]int{0, math.MinInt / 4, math.MinInt / 4}

	for _, num := range nums {
		prev := dp
		for r, total := range prev {
			next := (r + num) % 3
			if total+num > dp[next] {
				dp[next] = total + num
			}
		}
	}

	return dp[0]
}

/*
Explanation

dp[r] stores the largest sum seen so far with remainder r modulo 3. For each
number, either skip it or add it to a previous remainder class. Adding num to a
sum with remainder r moves it to (r+num)%3.

Only three states are needed because divisibility by 3 depends only on the
remainder. Copying dp into prev prevents using the same number more than once
in one iteration.

Edge cases: impossible remainders start as very negative values; answer may be
0; numbers already divisible by 3 accumulate in dp[0].

Time complexity: O(n).
Space complexity: O(1).
*/
