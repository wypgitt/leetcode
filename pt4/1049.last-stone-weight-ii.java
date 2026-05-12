/*
 * 1049. Last Stone Weight II
 */
class Solution {
    public int lastStoneWeightII(int[] stones) {
        int total = 0;
        for (int stone : stones) {
            total += stone;
        }

        int target = total / 2;
        boolean[] possible = new boolean[target + 1];
        possible[0] = true;

        for (int stone : stones) {
            for (int weight = target; weight >= stone; weight--) {
                possible[weight] = possible[weight] || possible[weight - stone];
            }
        }

        for (int weight = target; weight >= 0; weight--) {
            if (possible[weight]) {
                return total - 2 * weight;
            }
        }

        return 0;
    }
}

/*
Interview Explanation

Core idea:
All smash operations are equivalent to partitioning stones into two groups and
taking the absolute difference of group sums. We want the two sums as close as
possible.

Java data structures:
- boolean[] possible is a 0/1 knapsack table. possible[s] means some subset of
  stones has sum s.
- Backward iteration prevents using the same stone more than once.

Algorithm:
1. Compute total sum.
2. Find all reachable subset sums up to total / 2.
3. Choose the largest reachable sum weight <= total / 2.
4. Return total - 2 * weight.

Correctness:
Each final result can be represented by assigning every original stone a plus
or minus sign, which is the same as splitting stones into two groups. The
smallest possible final weight is the minimum difference between group sums.
The DP enumerates all possible sums for one group, and the closest sum to half
the total minimizes that difference.

Complexity:
Let S be total sum. Time is O(nS), space is O(S). Here S <= 3000.

Edge cases:
- One stone returns its weight.
- Perfect partition returns 0.
- Repeated weights are handled independently by the backward loop.
*/
