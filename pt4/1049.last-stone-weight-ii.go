package main

/*
1049. Last Stone Weight II
*/
func lastStoneWeightII(stones []int) int {
	total := 0
	for _, stone := range stones {
		total += stone
	}

	target := total / 2
	possible := make([]bool, target+1)
	possible[0] = true

	for _, stone := range stones {
		for weight := target; weight >= stone; weight-- {
			possible[weight] = possible[weight] || possible[weight-stone]
		}
	}

	for weight := target; weight >= 0; weight-- {
		if possible[weight] {
			return total - 2*weight
		}
	}

	return 0
}

/*
Interview Explanation

Core idea:
After all smashes, the final weight is equivalent to splitting stones into two
groups and taking the absolute difference of their sums. We want the two group
sums as close as possible.

Go data structures:
- []bool possible is a 0/1 knapsack table where possible[s] means some subset
  has sum s.
- Backward iteration ensures each stone is used at most once.

Algorithm:
1. Compute total sum.
2. Use subset-sum DP up to total/2.
3. Find the largest reachable weight not exceeding total/2.
4. Return total - 2*weight.

Correctness:
Each smash sequence can be represented as assigning each original stone a plus
or minus sign, equivalent to partitioning stones into two groups. The smallest
remaining weight is the smallest difference between group sums. The DP
enumerates all possible sums for one group, and choosing the one closest to
half the total minimizes that difference.

Complexity:
Let S be total sum. Time is O(n*S), space is O(S). Here S <= 3000.

Edge cases:
- One stone returns itself.
- Perfect partition returns 0.
- Repeated weights are handled independently by the backward loop.
*/
