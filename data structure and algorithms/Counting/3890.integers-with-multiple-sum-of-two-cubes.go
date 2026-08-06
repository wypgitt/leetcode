package leetcode

//
// @lc app=leetcode id=3890 lang=golang
//
// [3890] Integers With Multiple Sum of Two Cubes
//
// Notes
// Generate all sums a^3+b^3 <= n with 1 <= a <= b. Count how many pairs produce
// each sum, then return sorted sums with count at least two. Precomputing cubes
// avoids repeated multiplication. Time: O(cuberoot(n)^2). Space: O(number of
// sums).
//
// @lc code=start

import "sort"

func FindGoodIntegers3890(n int) []int {
	limit := 0
	for cube3890(limit+1) <= n {
		limit++
	}

	cubes := make([]int, limit+1)
	for value := 1; value <= limit; value++ {
		cubes[value] = cube3890(value)
	}

	sumToCount := map[int]int{}
	for a := 1; a <= limit; a++ {
		cubeA := cubes[a]
		for b := a; b <= limit; b++ {
			total := cubeA + cubes[b]
			if total > n {
				break
			}
			sumToCount[total]++
		}
	}

	answer := []int{}
	for total, count := range sumToCount {
		if count >= 2 {
			answer = append(answer, total)
		}
	}
	sort.Ints(answer)
	return answer
}

func cube3890(x int) int {
	return x * x * x
}

// @lc code=end
