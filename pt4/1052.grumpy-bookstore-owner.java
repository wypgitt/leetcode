/*
 * 1052. Grumpy Bookstore Owner
 */
class Solution {
    public int maxSatisfied(int[] customers, int[] grumpy, int minutes) {
        int alwaysSatisfied = 0;
        int extraSatisfied = 0;
        int bestExtra = 0;

        for (int i = 0; i < customers.length; i++) {
            if (grumpy[i] == 0) {
                alwaysSatisfied += customers[i];
            } else {
                extraSatisfied += customers[i];
            }

            if (i >= minutes && grumpy[i - minutes] == 1) {
                extraSatisfied -= customers[i - minutes];
            }

            bestExtra = Math.max(bestExtra, extraSatisfied);
        }

        return alwaysSatisfied + bestExtra;
    }
}

/*
Interview Explanation

Core idea:
Customers during non-grumpy minutes are already satisfied. The secret technique
only adds customers during grumpy minutes, so choose the length-minutes window
with the largest sum of otherwise-unsatisfied customers.

Java data structures:
- Primitive counters are enough.
- The fixed-size sliding window is represented by extraSatisfied and updated
  as the right boundary advances.

Algorithm:
1. Add all naturally satisfied customers to alwaysSatisfied.
2. Maintain the sum of grumpy-minute customers in the current window.
3. Remove the leftmost value when the window grows beyond minutes.
4. Add the best window gain to alwaysSatisfied.

Correctness:
For any chosen technique interval, the only new satisfied customers are those
with grumpy[i] == 1 inside that interval. The sliding window evaluates exactly
that gain for every possible interval of length minutes and chooses the
maximum, so the final total is optimal.

Complexity:
Time is O(n), space is O(1).

Edge cases:
- minutes equals n: all customers can be satisfied.
- No grumpy minutes: extra gain is 0.
- All grumpy minutes: this becomes maximum fixed-window sum.
*/
