package main

/*
1031. Maximum Sum of Two Non-Overlapping Subarrays
*/
func maxSumTwoNoOverlap(nums []int, firstLen int, secondLen int) int {
	prefix := make([]int, len(nums)+1)
	for i, num := range nums {
		prefix[i+1] = prefix[i] + num
	}

	bestWithOrder := func(leftLen, rightLen int) int {
		bestLeft := 0
		answer := 0

		for rightEnd := leftLen + rightLen; rightEnd <= len(nums); rightEnd++ {
			leftEnd := rightEnd - rightLen
			leftSum := prefix[leftEnd] - prefix[leftEnd-leftLen]
			if leftSum > bestLeft {
				bestLeft = leftSum
			}

			rightSum := prefix[rightEnd] - prefix[rightEnd-rightLen]
			if bestLeft+rightSum > answer {
				answer = bestLeft + rightSum
			}
		}

		return answer
	}

	firstBeforeSecond := bestWithOrder(firstLen, secondLen)
	secondBeforeFirst := bestWithOrder(secondLen, firstLen)
	if firstBeforeSecond > secondBeforeFirst {
		return firstBeforeSecond
	}
	return secondBeforeFirst
}

/*
Interview Explanation

Core idea:
The two subarrays can appear in either order. If we fix one order, then as we
scan the right subarray, we only need the best left subarray that ends before
it starts.

Go data structures:
- []int prefix supports O(1) range-sum queries.
- A closure reuses the same sweep logic for both possible orders.

Algorithm:
1. Build prefix sums.
2. Sweep with firstLen before secondLen.
3. Sweep with secondLen before firstLen.
4. Return the larger result.

Correctness:
For each possible right subarray, bestLeft is the maximum sum among all valid
left subarrays ending before it. Combining those gives the best pair for that
right position. Scanning all right positions covers every pair in that order,
and checking both orders covers all non-overlapping pairs.

Complexity:
Time is O(n), and space is O(n) for prefix sums.

Edge cases:
- The two windows exactly fill the array.
- Equal lengths are fine.
- nums are nonnegative, so zero initialization is safe.
*/
