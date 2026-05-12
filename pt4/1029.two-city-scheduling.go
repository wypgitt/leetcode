package main

import "sort"

/*
1029. Two City Scheduling
*/
func twoCitySchedCost(costs [][]int) int {
	sort.Slice(costs, func(i, j int) bool {
		return costs[i][0]-costs[i][1] < costs[j][0]-costs[j][1]
	})

	half := len(costs) / 2
	total := 0
	for i, cost := range costs {
		if i < half {
			total += cost[0]
		} else {
			total += cost[1]
		}
	}
	return total
}

/*
Interview Explanation

Core idea:
Imagine sending everyone to city B. Sending person i to city A instead changes
the cost by costA - costB. We need exactly n people in A, so choose the n
smallest changes.

Go data structures:
- sort.Slice orders people by their A-vs-B cost difference.
- Plain ints are enough for totals under the constraints.

Algorithm:
1. Sort by costA - costB.
2. Send the first half to city A.
3. Send the second half to city B.
4. Sum the selected costs.

Correctness:
If a person assigned to B has a smaller A-B difference than a person assigned
to A, swapping them cannot increase total cost. Therefore in some optimal
solution, the A group is exactly the first half in sorted difference order.
The algorithm constructs that assignment.

Complexity:
Sorting costs O(n log n) for 2n people. Extra space is O(1) aside from sorting
internals.

Edge cases:
- Two people only.
- Equal differences can be ordered either way.
- A-vs-B differences may be negative.
*/
