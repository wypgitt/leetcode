import java.util.Arrays;

/*
 * 1029. Two City Scheduling
 */
class Solution {
    public int twoCitySchedCost(int[][] costs) {
        Arrays.sort(costs, (a, b) -> Integer.compare(a[0] - a[1], b[0] - b[1]));

        int half = costs.length / 2;
        int total = 0;
        for (int i = 0; i < costs.length; i++) {
            total += i < half ? costs[i][0] : costs[i][1];
        }
        return total;
    }
}

/*
Interview Explanation

Core idea:
Imagine sending everyone to city B first. Sending person i to city A instead
changes the cost by aCost - bCost. We need exactly n people in A, so pick the
n smallest changes.

Java data structures:
- Arrays.sort orders the cost rows by their A-vs-B savings.
- Primitive ints are enough for the total because constraints are small.

Algorithm:
1. Sort by (costA - costB).
2. Send the first half to A.
3. Send the second half to B.
4. Sum the chosen costs.

Correctness:
If person x is sent to B and person y is sent to A, but x has a smaller
(A - B) difference than y, swapping them cannot increase cost. Therefore an
optimal solution sends the first n people in sorted difference order to A and
the rest to B. The algorithm constructs exactly that assignment.

Complexity:
Sorting O(n log n) for 2n people. Extra space is O(1) apart from sorting
overhead.

Edge cases:
- Only two people: the smaller difference goes to A.
- Equal differences can be in either order.
- Costs are positive but the difference can be negative.
*/
