package main

/*
1052. Grumpy Bookstore Owner
*/
func maxSatisfied(customers []int, grumpy []int, minutes int) int {
	alwaysSatisfied := 0
	extraSatisfied := 0
	bestExtra := 0

	for i, count := range customers {
		if grumpy[i] == 0 {
			alwaysSatisfied += count
		} else {
			extraSatisfied += count
		}

		if i >= minutes && grumpy[i-minutes] == 1 {
			extraSatisfied -= customers[i-minutes]
		}

		if extraSatisfied > bestExtra {
			bestExtra = extraSatisfied
		}
	}

	return alwaysSatisfied + bestExtra
}

/*
Interview Explanation

Core idea:
Customers during non-grumpy minutes are already satisfied. The secret
technique only adds value during grumpy minutes, so choose the length-minutes
window with the largest number of otherwise-unsatisfied customers.

Go data structures:
- Plain integer counters are enough.
- extraSatisfied represents the current fixed-size sliding-window gain.

Algorithm:
1. Add all non-grumpy customers to alwaysSatisfied.
2. Slide a window of length minutes across grumpy minutes.
3. The window sum counts only customers where grumpy[i] == 1.
4. Return alwaysSatisfied plus the best window gain.

Correctness:
For any chosen technique interval, the only newly satisfied customers are the
grumpy customers inside that interval. The sliding window evaluates exactly
that gain for every possible interval and chooses the maximum, so the final
answer is optimal.

Complexity:
Time is O(n), and space is O(1).

Edge cases:
- minutes == n satisfies everyone.
- No grumpy minutes gives zero extra gain.
- All grumpy minutes becomes maximum fixed-window sum.
*/
