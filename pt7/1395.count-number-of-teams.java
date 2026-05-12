/*
 * LeetCode 1395 - Count Number of Teams
 */
class Solution {
    public int numTeams(int[] rating) {
        int teams = 0;
        int n = rating.length;

        for (int middle = 0; middle < n; middle++) {
            int smallerLeft = 0;
            int greaterLeft = 0;
            int smallerRight = 0;
            int greaterRight = 0;

            for (int left = 0; left < middle; left++) {
                if (rating[left] < rating[middle]) {
                    smallerLeft++;
                } else {
                    greaterLeft++;
                }
            }

            for (int right = middle + 1; right < n; right++) {
                if (rating[right] > rating[middle]) {
                    greaterRight++;
                } else {
                    smallerRight++;
                }
            }

            teams += smallerLeft * greaterRight;
            teams += greaterLeft * smallerRight;
        }

        return teams;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Treat each soldier as the middle of a 3-person team. Increasing teams choose
 * a smaller rating on the left and a larger rating on the right. Decreasing
 * teams choose a larger rating on the left and a smaller rating on the right.
 *
 * Java data structures:
 * Four integer counters per middle index are enough. The constraints are small,
 * so no Fenwick tree or extra arrays are needed.
 *
 * Formula:
 * For middle j:
 * increasing = smallerLeft * greaterRight
 * decreasing = greaterLeft * smallerRight
 *
 * Edge cases:
 * - Fewer than three soldiers returns 0.
 * - Strictly increasing arrays count only increasing triples.
 * - Strictly decreasing arrays count only decreasing triples.
 *
 * Complexity:
 * Time O(n^2), acceptable for n <= 200.
 * Space O(1).
 */
