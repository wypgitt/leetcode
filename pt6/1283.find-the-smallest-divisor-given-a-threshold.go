package main

func smallestDivisor(nums []int, threshold int) int {
	right := 0
	for _, num := range nums {
		if num > right {
			right = num
		}
	}

	left := 1
	for left < right {
		mid := left + (right-left)/2
		if divisorSum(nums, mid) <= threshold {
			right = mid
		} else {
			left = mid + 1
		}
	}
	return left
}

func divisorSum(nums []int, divisor int) int {
	total := 0
	for _, num := range nums {
		total += (num + divisor - 1) / divisor
	}
	return total
}

/*
Explanation

For a fixed divisor d, the sum is sum(ceil(num/d)). As d increases, this sum
never increases. That monotonic predicate lets us binary search for the
smallest divisor with sum <= threshold.

Go detail: (num+divisor-1)/divisor is integer ceiling division for positive
integers.

Edge cases: divisor 1 gives the largest sum; max(nums) is a valid upper bound;
an exact threshold match still searches left for the smallest divisor.

Time complexity: O(n log max(nums)).
Space complexity: O(1).
*/
